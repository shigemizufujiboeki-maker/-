# 今のアプリ(index.html)から試験版(trial/index.html)を作り直す。使い方: python3 tools/make_trial.py index.html trial/index.html
# 元のアプリの文言が変わって見つからない所があると "NOT FOUND" で止まる。その時はこの中の置き換え文を直す。
import sys,re
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
def rep(old,new,count=None):
    global s
    n=s.count(old)
    if n==0: raise SystemExit('NOT FOUND: '+old[:80])
    if count is not None and n!=count: raise SystemExit(f'COUNT {n}!={count}: '+old[:80])
    s=s.replace(old,new)

# 1. 見出し・名前
rep('<title>FOB商談ノート v4.4｜広州交易会</title>','<title>FOB商談ノート 試験版</title>')
rep('<small>2026年10月 広州交易会｜端末保存・オフライン計算</small>','<small>試験版（見本データ入り）｜端末保存・オフライン計算</small>')
rep('FOB AI商談ノート <span','FOB AI商談ノート 試験版 <span')
rep("2026年10月 広州交易会　／　出力日：","展示会　／　出力日：")
s=s.replace('広州交易会','展示会')

# 2. 会社紹介フレーズ（架空の会社に）
rep('<h2>不二貿易の紹介｜商談でそのまま使える7フレーズ</h2>','<h2>自社の紹介｜商談でそのまま使える7フレーズ（見本：サンプル商事は架空の会社です。自社名に置き換えてください）</h2>')
rep('不二貿易株式会社と申します。日本から来ました。','サンプル商事株式会社と申します。日本から来ました。')
rep('We are Fuji Boeki Co., Ltd., a trading company from Japan.','We are Sample Trading Co., Ltd., a trading company from Japan.')
rep('ウィー アー フジ ボウエキ カンパニー リミテッド、ア トレーディング カンパニー フロム ジャパン。','ウィー アー サンプル トレーディング カンパニー リミテッド、ア トレーディング カンパニー フロム ジャパン。')
rep('我们是不二贸易株式会社，来自日本。','我们是Sample商事株式会社，来自日本。')
rep('ウォーメン シー ブーアル マオイー ジュシーフイシャー、ライツー リーベン。','ウォーメン シー サンプル シャンシー ジュシーフイシャー、ライツー リーベン。')
rep("不二貿易の取扱商材と日本国内の販路を短く説明します。","自社の取扱商材と日本国内の販路を短く説明します。")
# 取引先名
m=re.search(r'<span>イオン、カインズ、ニトリなどの大手量販店と取引があります。</span>.*?</details>',s,re.S)
if not m: raise SystemExit('company4 not found')
blk=m.group(0)
new_blk=('<span>日本の大手小売チェーンと取引があります。</span></summary><div class="phrasebody">'
 '<div class="qlang">English</div><div class="qsentence" lang="en">We do business with major retail chains in Japan.</div>'
 '<div class="qreading">ウィー ドゥー ビジネス ウィズ メイジャー リーテイル チェインズ イン ジャパン。</div>'
 '<div class="qlang">中文（普通话）</div><div class="qsentence" lang="zh-CN">我们与日本的大型连锁零售商有业务往来。</div>'
 '<div class="qreading">ウォーメン ユー リーベン ダ ダーシン リエンスオ リンショウシャン ヨウ イエウ ワンライ。</div></div></details>')
s=s.replace(blk,new_blk)

# 3. 報告書：本人用モード・社内の宛先を外す
rep('<option value="shigemizu">重水用モード（10月23日提出版に準拠）</option>','')
rep('<input id="reportTo" value="田坂社長 様">','<input id="reportTo" placeholder="例：営業部長 様">')
rep('<input id="reportDept" value="ビジネスクリエーション事業部">','<input id="reportDept" placeholder="例：営業部">')
rep("const presets={reportTo:'田坂社長 様',reportDept:'ビジネスクリエーション事業部',reportName:'重水 脩'};","const presets={reportTo:'',reportDept:'',reportName:''};")
rep("mode.value=saved==='shigemizu'?'shigemizu':'general';","mode.value='general';")
s=s.replace('10月23日提出版を参考に、','')
s=s.replace('10月23日の提出版を参考にした','社内報告書の')

# 4. 保存場所・オフラインの仕組みを今のアプリと分ける
rep("indexedDB.open('guangzhou-fob-deals-v1',2)","indexedDB.open('trial-fob-deals-v1',2)",1)
s=s.replace("'fobReportMode'","'trialReportMode'").replace("'fobReport_'","'trialReport_'")
rep("caches.open('guangzhou-fob-cache-v25')","caches.open('trial-fob-cache-v1')",1)

# 5. 計算の数字を設定へ
COST_JS=r"""
// 試験版：計算に使う数字は設定画面で変えられる（この端末だけに保存）
const COST_DEFAULTS={fx:150,markup:3,margin:25,cap:2400};
function costSettings(){let v={};try{v=JSON.parse(localStorage.getItem('trialCostSettings')||'{}')}catch(e){}const o={...COST_DEFAULTS};for(const k in COST_DEFAULTS){const n=Number(v[k]);if(v[k]!==undefined&&v[k]!==''&&Number.isFinite(n))o[k]=n}if(!(o.fx>0))o.fx=COST_DEFAULTS.fx;if(!(o.cap>0))o.cap=COST_DEFAULTS.cap;if(!(o.margin>=0&&o.margin<100))o.margin=COST_DEFAULTS.margin;if(!(o.markup>=0))o.markup=COST_DEFAULTS.markup;return o}
const FX=()=>costSettings().fx,UPLIFT=()=>1+costSettings().markup/100,KEEP=()=>1-costSettings().margin/100,CAP=()=>costSettings().cap;
function costSummary(){const c=costSettings();return `1 USD=${c.fx}円、FOB上乗せ${c.markup}%、コンテナ容量${c.cap.toLocaleString('ja-JP')}才、目標粗利率${c.margin}%`}
function costFormula(){const c=costSettings();return `FOB × ${c.fx} × ${UPLIFT().toFixed(4).replace(/0+$/,'').replace(/\.$/,'')} ÷ ${KEEP().toFixed(4).replace(/0+$/,'').replace(/\.$/,'')}`}
function costSettingsInit(){const ids={fx:'setFx',markup:'setMarkup',margin:'setMargin',cap:'setCap'};const c=costSettings();for(const k in ids){const el=document.getElementById(ids[k]);if(!el)continue;el.value=c[k];el.addEventListener('input',()=>{const v={};for(const kk in ids)v[kk]=document.getElementById(ids[kk]).value;try{localStorage.setItem('trialCostSettings',JSON.stringify(v))}catch(e){}costRefresh()})}const r=document.getElementById('setReset');if(r)r.onclick=()=>{try{localStorage.removeItem('trialCostSettings')}catch(e){}const d=costSettings();for(const k in ids)document.getElementById(ids[k]).value=d[k];costRefresh()};costRefresh()}
function costRefresh(){document.querySelectorAll('.costSummary').forEach(e=>e.textContent=costSummary());document.querySelectorAll('.costFormula').forEach(e=>e.textContent=costFormula());try{calc()}catch(e){}try{multiRender()}catch(e){}}
"""
# 計算式
rep("const cost=fob===null?null:fob*170*1.05;","const cost=fob===null?null:fob*FX()*UPLIFT();",1)
rep("carton=Math.floor(2200/sai);","carton=Math.floor(CAP()/sai);",1)
rep("toNum('ocean')*170/qty","toNum('ocean')*FX()/qty",1)
rep("(cost+ocean+domestic+duty+other)/.7","(cost+ocean+domestic+duty+other)/KEEP()",1)
rep("fmt(cost/.7)+'円'","fmt(cost/KEEP())+'円'",1)
rep("`FOB円換算＋5%：","`FOB円換算＋上乗せ：",1)
rep("`下代は原価÷0.7、円単位切り上げ。","`下代は原価÷(1−目標粗利率)、円単位切り上げ（${costSummary()}）。",1)
rep('const cartons=Math.floor(2200/sai);','const cartons=Math.floor(CAP()/sai);',1)
rep('const cost=n[0]*170*1.05;return Math.ceil(Number((((cost+cost*n[7]/100+n[5]*170/qty+n[6]/qty+n[8])/.7)).toFixed(8)))',
    'const cost=n[0]*FX()*UPLIFT();return Math.ceil(Number((((cost+cost*n[7]/100+n[5]*FX()/qty+n[6]/qty+n[8])/KEEP())).toFixed(8)))',1)
rep("Math.ceil(Number((v*170*1.05/.7).toFixed(8)))","Math.ceil(Number((v*FX()*UPLIFT()/KEEP()).toFixed(8)))",1)
rep("FOB下代一次試算：FOB × 170 × 1.05 ÷ 0.7。","FOB下代一次試算：<span class=\"costFormula\"></span>（数字は「計算の設定」で変更）。",1)
rep("社内試算：1 USD=170円、FOB+5%、40FHQ=2,200才、目標粗利30%。","試算の前提：'+escapeText(costSummary())+'。",1)
SETTINGS_HTML=('<details id="costSettingsCard"><summary><strong>計算の設定（為替・上乗せ率・粗利率・コンテナ容量）</strong></summary>'
 '<p class="note">下代の計算に使う数字です。最初は見本の値が入っています。入れた数字はこの端末だけに保存されます。</p>'
 '<div class="grid">'
 '<div class="field"><label>為替（円／USD）</label><input id="setFx" type="number" inputmode="decimal" step="0.01" min="0"></div>'
 '<div class="field"><label>FOBへの上乗せ率（％）</label><input id="setMarkup" type="number" inputmode="decimal" step="0.1" min="0"></div>'
 '<div class="field"><label>目標粗利率（％）</label><input id="setMargin" type="number" inputmode="decimal" step="0.1" min="0" max="99"></div>'
 '<div class="field"><label>コンテナ1本に積める量（才）</label><input id="setCap" type="number" inputmode="numeric" step="1" min="1"></div>'
 '</div><p class="note">いまの前提：<span class="costSummary"></span>。1才＝0.0278㎥で計算します。</p>'
 '<div class="btnrow"><button type="button" id="setReset" class="secondary">見本の値に戻す</button></div></details>')
rep('<p class="note">固定：為替・海上運賃換算170円／USD、40FHQ＝2,200才、1才＝0.0278㎥、FOB上乗せ5％、粗利率30％。</p></section>',
    '<p class="note">前提：<span class="costSummary"></span>（画面上の「計算の設定」で変更できます）。</p></section>',1)

# 6. 見本データ
SAMPLE_JS=r"""
// 試験版：架空の見本データ（実在の会社・商品ではありません）
function loadSampleData(){if(multiItems.length&&!confirm('いま入力中の商品に、見本の商品3つを追加します。よろしいですか？'))return;const mk=document.getElementById('maker');if(mk&&!mk.value)mk.value='Sample Home Goods Co.（架空）';
[{sku:'SMP-001',name:'木製スツール（見本）',fob:'8.5',moq:'300',width:'40',depth:'40',height:'48',pack:'2',lead:'45日',material:'天然木',notes:'架空の見本データ'},
 {sku:'SMP-002',name:'収納バスケット3点セット（見本）',fob:'4.2',moq:'500',width:'45',depth:'35',height:'30',pack:'6',lead:'30日',material:'ペーパーコード',notes:'架空の見本データ'},
 {sku:'SMP-003',name:'LEDデスクライト（見本）',fob:'6.8',moq:'1000',width:'52',depth:'38',height:'40',pack:'10',lead:'40日',material:'ABS樹脂・アルミ',notes:'架空の見本データ'}
].forEach(d=>multiItems.push({...multiBlank(),...d}));normaliseItemNumbers();
const setIf=(id,v)=>{const e=document.getElementById(id);if(e&&e.value==='')e.value=v};setIf('ocean','3000');setIf('domestic','120000');setIf('tariff','0');setIf('other','10');
multiExpandedId=null;multiRender();markMultiDirty();try{calc()}catch(e){}const st=document.getElementById('sampleState');if(st)st.textContent='見本の商品3つと、運賃などの見本の値を入れました（すべて架空です）。'}
"""
SAMPLE_HTML=('<section class="card" id="sampleCard"><h2>試験版の使い方</h2>'
 '<p class="note">これは試験版です。中のデータは架空です。まず「見本データを入れる」を押すと、商品3つが入り、下代の計算を試せます。計算に使う数字は、下の「計算の設定」を開いて自社の数字に変えてください。</p>'
 '<div class="btnrow"><button type="button" id="sampleLoad">見本データを入れる</button></div><p class="note" id="sampleState"></p>'+SETTINGS_HTML+'</section>')
# 最初のページ（STEP 1）の前に置く
rep('未接続の場合はChatGPTへの転記方式です。</div>','未接続の場合はChatGPTへの転記方式です。</div>'+SAMPLE_HTML,1)

# JS を最初の <script> の先頭に差し込み、初期化を load 時に
i=s.find('<script>')
if i<0: raise SystemExit('script tag')
s=s[:i+8]+COST_JS+SAMPLE_JS+"\nwindow.addEventListener('DOMContentLoaded',()=>{try{costSettingsInit()}catch(e){console.error(e)}const b=document.getElementById('sampleLoad');if(b)b.onclick=loadSampleData});\n"+s[i+8:]


# 開いた直後に保存場所の準備前に読みに行く不具合（元のアプリにもある）を直す
rep("function getAll(){return new Promise((res,rej)=>{const q=tx('readonly')","async function getAll(){if(!db)db=await openDB();return new Promise((res,rej)=>{const q=tx('readonly')",1)
# 本人用モードの名前を中立に
s=s.replace("'shigemizu'","'custom'")

# 7. 残っていないか確かめる
bad=['不二','Fuji Boeki','イオン','AEON','カインズ','CAINZ','Cainz','ニトリ','Nitori','永旺','宜得利','重水','田坂','ビジネスクリエーション','shigemizu','*170','170円','×170','× 170','1.05','/.7',"guangzhou-fob-deals",'2200']
left=[b for b in bad if b in s]
open(dst,'w',encoding='utf-8').write(s)
print('remaining:',left)
