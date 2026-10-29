(async function () {
  'use strict';
  const root = document.getElementById('assembly-workbench');
  const $ = id => root.querySelector('#' + id);
  const STORAGE = 'myMicrobyte-v08-assembly-guide-v1';
  const CAP_NAMES = [];
  const CAPS = CAP_NAMES.map(n => 'Button_' + n);
  const VARIANTS={raised:{name:'A · 凸起屏幕框',note:'屏幕框高于按键区 1.2 mm，可挡住靠近玻璃的手指；玻璃相对框顶下陷约 1.9 mm。'},flat:{name:'B · 平面前盖',note:'屏幕框与按键区同高，玻璃相对前盖下陷约 0.7 mm；按键预计露出约 1.4 mm。'}};
  const UPPER = ['front','inserts'];
  const ALL = ['front','rear',...CAPS,'pcb','slider','battery','speaker','lid','inserts','screws'];
  const ACOUSTIC = ['rear','speaker','lid'];
  const PRINTED = ['front','rear','slider','lid'];
  const FILAMENTS = {"pla_silver": {"name": "银色 PLA", "color": "#a6aaad", "material": "PLA", "stock": "备用 1 卷", "metalness": 0.22}, "pla_black": {"name": "黑色 PLA", "color": "#202329", "material": "PLA", "stock": "当前槽 4"}, "pla_red": {"name": "红色 PLA", "color": "#c71f29", "material": "PLA", "stock": "备用 1 卷"}, "pla_yellow": {"name": "黄色 PLA", "color": "#f0cb12", "material": "PLA", "stock": "备用 1 卷"}, "pla_blue": {"name": "蓝色 PLA", "color": "#1743ac", "material": "PLA", "stock": "当前槽 1"}, "pla_green": {"name": "绿色 PLA", "color": "#12a14c", "material": "PLA", "stock": "当前槽 2"}, "petg_white": {"name": "白色 PETG", "color": "#eeeee8", "material": "PETG", "stock": "2 卷"}, "petg_gray": {"name": "灰色 PETG", "color": "#8b8e91", "material": "PETG", "stock": "2 卷"}, "petg_black": {"name": "黑色 PETG", "color": "#202329", "material": "PETG", "stock": "2 卷"}, "petg_clear": {"name": "透明 PETG", "color": "#d9e6e8", "material": "PETG", "stock": "3 卷；当前槽 3", "opacity": 0.38}};
  const PALETTES = {"silver_red": {"name": "银黑红 · 推荐", "filaments": {"front": "pla_silver", "rear": "pla_black", "slider": "pla_red", "lid": "pla_black"}, "note": "需换入银色、红色 PLA；黑色沿用槽 4。", "colors": {"front": "#a6aaad", "rear": "#202329", "slider": "#c71f29", "lid": "#202329"}}, "black_green": {"name": "黑绿 · 无需换卷", "filaments": {"front": "pla_black", "rear": "pla_black", "slider": "pla_green", "lid": "pla_black"}, "note": "当前槽 2 绿色、槽 4 黑色 PLA 即可。", "colors": {"front": "#202329", "rear": "#202329", "slider": "#12a14c", "lid": "#202329"}}, "blue_green": {"name": "蓝黑绿 · 无需换卷", "filaments": {"front": "pla_blue", "rear": "pla_black", "slider": "pla_green", "lid": "pla_black"}, "note": "当前槽 1 蓝色、槽 2 绿色、槽 4 黑色 PLA 即可。", "colors": {"front": "#1743ac", "rear": "#202329", "slider": "#12a14c", "lid": "#202329"}}, "yellow_red": {"name": "黄黑红 · 明亮", "filaments": {"front": "pla_yellow", "rear": "pla_black", "slider": "pla_red", "lid": "pla_black"}, "note": "需换入黄色、红色 PLA；黑色沿用槽 4。", "colors": {"front": "#f0cb12", "rear": "#202329", "slider": "#c71f29", "lid": "#202329"}}, "red_yellow": {"name": "红黑黄 · 复古", "filaments": {"front": "pla_red", "rear": "pla_black", "slider": "pla_yellow", "lid": "pla_black"}, "note": "需换入红色、黄色 PLA；黑色沿用槽 4。", "colors": {"front": "#c71f29", "rear": "#202329", "slider": "#f0cb12", "lid": "#202329"}}, "green_blue": {"name": "绿黑蓝 · 无需换卷", "filaments": {"front": "pla_green", "rear": "pla_black", "slider": "pla_blue", "lid": "pla_black"}, "note": "当前槽 1 蓝色、槽 2 绿色、槽 4 黑色 PLA 即可。", "colors": {"front": "#12a14c", "rear": "#202329", "slider": "#1743ac", "lid": "#202329"}}, "white_gray": {"name": "白灰黑 · 全 PETG", "filaments": {"front": "petg_white", "rear": "petg_gray", "slider": "petg_black", "lid": "petg_gray"}, "note": "需换入白、灰、黑 PETG，并使用对应 PETG 配置。", "colors": {"front": "#eeeee8", "rear": "#8b8e91", "slider": "#202329", "lid": "#8b8e91"}}, "gray_black": {"name": "灰黑白 · 全 PETG", "filaments": {"front": "petg_gray", "rear": "petg_black", "slider": "petg_white", "lid": "petg_black"}, "note": "需换入灰、黑、白 PETG，并使用对应 PETG 配置。", "colors": {"front": "#8b8e91", "rear": "#202329", "slider": "#eeeee8", "lid": "#202329"}}, "clear_back": {"name": "黑透白 · 全 PETG", "filaments": {"front": "petg_black", "rear": "petg_clear", "slider": "petg_white", "lid": "petg_clear"}, "note": "透明 PETG 在槽 3；另需黑、白 PETG。后盖为磨砂透光示意。", "colors": {"front": "#202329", "rear": "#d9e6e8", "slider": "#eeeee8", "lid": "#d9e6e8"}}};
  const META = {
front:{name:'前盖（A / B）',description:'玻璃全周让空，不再有压在玻璃上方的内沿；侧定位名义间隙0.6 mm。常规按键孔6.6 mm，A键6.8 mm。十字区仍连通，避免悬空中心片。两种前盖使用同一后盖和PCB位置。'},
rear:{name:'后盖',description:'后部四处0.9 mm矮脚，声孔外侧浅槽通向边缘。电池框52×30 mm。音腔侧弹片固定喇叭，开窗盖可拆；拨帽导轨增加两处防脱弹片。'},
pcb:{name:'PCB 与屏幕',description:'PCB背面Z=9.0 mm，厚1.6 mm；屏幕胶层按1.0 mm、玻璃厚1.9 mm展示。玻璃顶面Z≈13.5 mm；静音开关名义顶面Z≈15.6 mm。本轮不垫高玻璃。'},
slider:{name:'加长防脱拨帽',description:'内侧横边长10.4 mm（旧6.8 mm），叉槽宽1.65 mm（旧1.95 mm）。先对准白拨杆，轻向外拨两处后盖弹片，放入并释放。前盖合上后进一步限制上浮；机械范围3.6 mm，实际电气两档需试装。'},
battery:{name:'3 mm 电池占位',description:'成品含保护板、包边建议≤51×29×3.3 mm，电池框52×30 mm。型号尚未定。'},
speaker:{name:'1510 喇叭',description:'15×10×3.5 mm，发声面朝后盖。侧弹片只夹硬边框。新增矮脚维持桌面出声间隙；盖上变小声的机理尚未实测确定。'},
lid:{name:'开窗音腔盖',description:'保留挂钩和双卡扣，中央约9×14.4 mm大开窗，线槽扩到3.2 mm。可拆下比较，无胶。它是通气固定框，不是密闭或调谐音箱。'},
inserts:{name:'热熔螺母 ×4',description:'M2×2×3，安装后端面不突出柱底，不让螺母顶住PCB。'},
screws:{name:'M2×5 螺丝 ×4',description:'先确认自然合拢，再交叉轻拧。用黑色画面检查玻璃有无泛白，分别按MENU/A/B观察。'}
  };
  const STEPS = [
    {title:'检查四件打印件', text:'前盖、后盖、拨帽和开窗音腔盖。此版不需要软密封圈或胶带。', checks:['清理音腔卡扣、弹片及走线槽的毛边。','PLA 可试装；频繁拆装时更推荐 PETG 后盖。'], visible:ALL, focus:'rear', view:'iso'},
    {title:'先装热熔螺母', text:'四个 M2×2×3 螺母装入前盖柱孔，放平冷却。', checks:['端面不凸出柱底。'], visible:['front','inserts'], moving:['inserts'], vector:[0,0,-12], focus:'inserts', view:'inside'},
    {title:'装入喇叭', text:'轻拨两侧弹片，发声面朝后盖放入，让硬边框平贴承台。', checks:['弹片只夹硬侧壁，不压振膜或背部透气孔。','静止模型显示弹片未变形位置；装入时约需向外让 0.3 mm。','轻晃检查是否松动，实际夹持力需试装。'], visible:['rear','speaker'], moving:['speaker'], vector:[0,0,12], focus:'speaker', detail:'acoustic', view:'iso'},
    {title:'挂入并扣上开窗盖', text:'线束从 3.2 mm 槽引出，盖子约倾斜 6° 滑入后方挂钩，再压低前边扣住两处卡扣。', checks:['前卡扣约需外让 0.25 mm，禁止硬撬。','动画示意腔盖路径，未模拟塑料弹性变形。','不用胶；线槽与硬接缝仍有漏气，不能视作气密音箱。'], visible:ACOUSTIC, moving:['lid'], motion:'hook', vector:[0,0,14], focus:'lid', detail:'acoustic', view:'iso'},
    {title:'固定薄电池', text:'沿用原有电池安装方案；本次免胶要求针对喇叭和音腔盖。', checks:['电池框净空 52 × 30 mm；成品含包边建议 ≤51 × 29 × 3.3 mm。','线束避开卡扣、螺丝柱和 PCB 元件。'], visible:[...ACOUSTIC,'battery'], moving:['battery'], vector:[0,0,17], focus:'battery', view:'iso'},
    {title:'将 PCB 放入后盖', text:'音腔扣好后放 PCB，屏幕向上，四角孔对齐支柱。', checks:['确认 PCB 平稳落在支柱上。','不要夹住喇叭线。'], visible:[...ACOUSTIC,'battery','pcb'], moving:['pcb'], vector:[0,0,24], focus:'pcb', view:'iso'},
    {title:'从上方装入拨帽', text:'纹路朝外，沿敞口导轨落下，叉槽套住白色拨杆，轻拨后盖两处防脱弹片再放入。', checks:['轻向外拨防脱弹片约 0.3 mm，放入后松开；动画未模拟弹片变形。','机械行程 3.6 mm；电气两档需实物确认。'], visible:['rear','pcb','slider','lid'], moving:['slider'], vector:[0,0,12], focus:'slider', view:'side'},
    {title:'合拢前盖', text:'对准屏幕、静音开关和 TF 唇边，轻放前盖。', checks:['不得用螺丝强压明显干涉。','检查按键、玻璃和 TF 插拔。'], visible:ALL.filter(id=>id!=='screws'), moving:UPPER, vector:[0,0,30], focus:'front', view:'iso'},
    {title:'装入四颗螺丝', text:'从后盖装入 M2×5，交叉均匀轻拧。', checks:['确认壳体自然合拢。'], visible:ALL, moving:['screws'], vector:[0,0,-15], focus:'screws', view:'bottom'},
    {title:'试听和检查', text:'以相同音源、音量对比有盖与无盖。拆盖前先取 PCB，轻向外拨前卡扣，抬起前边后退出固定挂钩。', checks:['分别测试开窗盖和无盖，手持和桌面平放；不预设音量一定增加。','卡扣韧性、夹持力和是否异响均需试装。'], visible:ALL, focus:'front', view:'iso'}
  ];
  const state = {variant:'raised',lidMode:'vented',detail:null,mode:'free', step:0, progress:100, explode:65, selected:'front', acoustic:false, palette:'black_green', colors:{...PALETTES.black_green.colors}, filaments:{...PALETTES.black_green.filaments}, transparent:false, labels:true, view:'iso', press:0, slide:0, hidden:[], offsets:{}, notes:{}, checked:[]};
  const clamp = (v,min,max,fallback=0) => Number.isFinite(Number(v)) ? Math.max(min,Math.min(max,Number(v))) : fallback;
  function loadState(raw) {
    if (!raw || raw.schema !== 'myMicrobyte.assembly.v1' || raw.model !== 'v0.8') return false;
    const s=raw.state;
    if (!s || typeof s!=='object') return false;
    state.variant=s.variant==='flat'?'flat':'raised';state.lidMode=s.lidMode==='off'?'off':'vented';state.detail=null;
    state.mode=s.mode==='guide'?'guide':'free'; state.step=Math.round(clamp(s.step,0,STEPS.length-1));
    state.progress=clamp(s.progress,0,100,100); state.explode=clamp(s.explode,0,100,35);
    state.selected=ALL.includes(s.selected)?s.selected:'front';
    state.acoustic=!!s.acoustic;state.palette=Object.hasOwn(PALETTES,s.palette)?s.palette:'custom';state.filaments={...PALETTES.silver_red.filaments};for(const id of PRINTED)if(Object.hasOwn(FILAMENTS,s.filaments?.[id]))state.filaments[id]=s.filaments[id];state.colors=Object.fromEntries(PRINTED.map(id=>[id,FILAMENTS[state.filaments[id]].color]));state.transparent=!!s.transparent;state.labels=s.labels!==false;
    state.view=['iso','top','inside','bottom','side','tf','height'].includes(s.view)?s.view:'iso';
    state.press=clamp(s.press,0,.6);state.slide=clamp(s.slide,-.55,3.05);
    state.hidden=Array.isArray(s.hidden)?s.hidden.filter(id=>ALL.includes(id)):[];
    state.checked=Array.isArray(s.checked)?s.checked.filter(n=>Number.isInteger(n)&&n>=0&&n<STEPS.length):[];
    state.offsets={};state.notes={};
    for(const id of ALL){
      if(Array.isArray(s.offsets?.[id])&&s.offsets[id].length===3)state.offsets[id]=s.offsets[id].map(v=>clamp(v,-30,30));
      if(typeof s.notes?.[id]==='string')state.notes[id]=s.notes[id].slice(0,1000);
    }
    return true;
  }
  try{loadState(JSON.parse(localStorage.getItem(STORAGE)));}catch(e){}
  const record = () => ({schema:'myMicrobyte.assembly.v1', model:'v0.8', savedAt:new Date().toISOString(), units:'mm', coordinates:'Original CAD world axes: X long side, Y short side, Z thickness. Translation only; no CAD rebuild or collision check.', state, adjustments:ALL.filter(id=>state.notes[id]||state.offsets[id]?.some(v=>v!==0)).map(id=>({part:id,name:META[id].name,translationMm:state.offsets[id]||[0,0,0],note:state.notes[id]||''}))});
  function save(){try{localStorage.setItem(STORAGE,JSON.stringify(record()));$('save-state').textContent='已保存到本机浏览器 · 可导出备份';}catch(e){$('save-state').textContent='浏览器未允许本地保存，请导出记录';}}
  function notify(text){$('notice').textContent=text;}
  let meshes=[],groups={},scene,camera,renderer,controls,selectionBox,animation=0;
  const host=$('canvas-host'), labelElements={};
  try {
    const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
    const packed=decode(document.getElementById('geometry').textContent.trim());
    const stream=new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'));
    const data=JSON.parse(await new Response(stream).text());
    scene=new THREE.Scene(); camera=new THREE.PerspectiveCamera(34,1,.1,2000);camera.up.set(0,0,1);
    renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0,0);
    renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;
    renderer.domElement.setAttribute('aria-label','myMicrobyte 3D 装配模型');host.appendChild(renderer.domElement);
    controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=12;controls.maxDistance=650;
    scene.add(new THREE.AmbientLight(0xffffff,1.4));
    for(const [pos,intensity] of [[[-75,-95,145],2.0],[[90,80,50],1.0],[[0,0,-100],.7]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...pos);scene.add(light);}
    for(const id of ALL){
      const group=new THREE.Group();group.name=id;scene.add(group);groups[id]=group;
      const option=document.createElement('option');option.value=id;option.textContent=META[id].name;$('part').appendChild(option);
      const row=document.createElement('div');row.className='part-row';
      const check=document.createElement('input');check.type='checkbox';check.checked=true;check.setAttribute('aria-label','显示'+META[id].name);check.dataset.part=id;
      const button=document.createElement('button');button.textContent=META[id].name;button.dataset.part=id;button.setAttribute('aria-pressed','false');
      row.append(check,button);$('part-list').appendChild(row);
      check.addEventListener('change',()=>{state.hidden=check.checked?state.hidden.filter(x=>x!==id):[...new Set([...state.hidden,id])];apply();save();});
      button.addEventListener('click',()=>select(id));
    }
    const classify=item=>item.type==='cap'?item.name:['pcb','component','lcd'].includes(item.type)?'pcb':item.type==='insert'?'inserts':item.type==='screw'?'screws':item.type;
    for(const item of data){
      const raw=new Int16Array(decode(item.p).buffer),positions=Float32Array.from(raw,v=>v/100);
      let geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(positions,3));geo.setIndex(new THREE.BufferAttribute(new Uint32Array(decode(item.i).buffer),1));
      const flat=geo.toNonIndexed();geo.dispose();geo=flat;geo.computeVertexNormals();geo.computeBoundingBox();
      const material=new THREE.MeshStandardMaterial({color:item.color,roughness:item.type==='lcd'?.3:.62,metalness:['insert','screw'].includes(item.type)?.48:.03,side:THREE.DoubleSide});
      const mesh=new THREE.Mesh(geo,material);mesh.userData={id:classify(item),type:item.type,name:item.name,variant:item.variant};groups[mesh.userData.id].add(mesh);meshes.push(mesh);
    }
    for(const id of ALL){
      const box=new THREE.Box3().setFromObject(groups[id]);groups[id].userData={box,center:box.getCenter(new THREE.Vector3()),size:box.getSize(new THREE.Vector3())};
      if(['front','rear','pcb','battery','speaker','slider','lid'].includes(id)){
        const label=document.createElement('div');label.className='model-label';label.textContent=META[id].name;$('labels').appendChild(label);labelElements[id]=label;
      }
    }
    selectionBox=new THREE.BoxHelper(groups.front,0x438bdd);selectionBox.material.transparent=true;selectionBox.material.opacity=.8;scene.add(selectionBox);
    for(let i=0;i<STEPS.length;i++){
      const option=document.createElement('option');option.value=i;option.textContent=`${i+1}. ${STEPS[i].title}`;$('step').appendChild(option);
      const button=document.createElement('button');button.textContent=i+1;button.setAttribute('aria-label',`${i+1}. ${STEPS[i].title}`);button.dataset.step=i;button.addEventListener('click',()=>chooseStep(i));$('step-dots').appendChild(button);
    }
    $('parts-total').textContent=`${ALL.length} 组 / ${data.length} 个实体`;
    function renderLabels(){
      const occupied=[];
      // The chosen part gets priority; hide overlapping labels instead of cluttering the model.
      for(const id of Object.keys(labelElements).sort((a,b)=>(b===state.selected)-(a===state.selected))){
        const el=labelElements[id],g=groups[id];
        if(!state.labels||!g.visible||!g.children.some(m=>m.visible)){el.hidden=true;continue;}
        const p=g.localToWorld(g.userData.center.clone()).project(camera);
        const x=(p.x+1)/2*host.clientWidth,y=(-p.y+1)/2*host.clientHeight;
        const hidden=p.z>1||p.z< -1||x<65||x>host.clientWidth-65||y<58||y>host.clientHeight-45||occupied.some(([px,py])=>Math.abs(px-x)<115&&Math.abs(py-y)<30);
        el.hidden=hidden;if(hidden)continue;
        occupied.push([x,y]);el.style.left=x+'px';el.style.top=y+'px';el.classList.toggle('selected',id===state.selected);
      }
    }
    function render(){if(!renderer)return;renderer.render(scene,camera);renderLabels();}
    function resize(){const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render();}
    function currentBox(){const box=new THREE.Box3();scene.updateMatrixWorld(true);for(const mesh of meshes)if(mesh.visible&&mesh.parent.visible)box.union(new THREE.Box3().setFromObject(mesh));return box.isEmpty()?groups.front.userData.box.clone():box;}
    const directions={iso:[90,-120,112],top:[0,-.001,1],inside:[55,-65,-120],bottom:[55,-75,-115],side:[140,-14,30],tf:[0,150,24],height:[15,-140,14]};
    function fit(view=state.view){
      let box=currentBox();
      if(state.detail==='slider')box=new THREE.Box3(new THREE.Vector3(34,-14,4),new THREE.Vector3(46,4,12));
      if(state.mode==='guide'&&STEPS[state.step].focus==='slider')box=new THREE.Box3(new THREE.Vector3(34,-13,4),new THREE.Vector3(46,2,25));
      if((state.mode==='free'&&state.acoustic)||(state.mode==='guide'&&STEPS[state.step].detail==='acoustic')){
        let high=10;for(const id of ACOUSTIC.filter(x=>x!=='rear'))if(groups[id].visible)high=Math.max(high,new THREE.Box3().setFromObject(groups[id]).max.z);
        box=new THREE.Box3(new THREE.Vector3(22,-15,0),new THREE.Vector3(39,10,high+1));
      }
      const center=box.getCenter(new THREE.Vector3()),dir=new THREE.Vector3(...directions[view]).normalize();
      controls.target.copy(center);camera.position.copy(center).add(dir);camera.lookAt(center);camera.updateMatrixWorld();
      const inverse=camera.matrixWorldInverse.clone(),tan=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
      let distance=30;
      for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
        const v=new THREE.Vector3(x,y,z).applyMatrix4(inverse);distance=Math.max(distance,Math.abs(v.y)/tan+v.z+1,Math.abs(v.x)/(tan*camera.aspect)+v.z+1);
      }
      camera.position.copy(center).addScaledVector(dir,distance*1.10);controls.update();render();
    }
    function explodedOffset(id,e){
      return [id==='slider'?e*17:0,0,e*(id==='front'||id==='inserts'?78:id==='pcb'?46:id==='lid'?30:id==='speaker'?12:id==='battery'?6:id==='screws'?-24:0)];
    }
    function updateInspector(){
      const id=state.selected,meta=META[id],size=id==='front'?new THREE.Box3().setFromObject(groups.front.children.find(m=>m.userData.variant===state.variant)).getSize(new THREE.Vector3()):groups[id].userData.size,offset=state.offsets[id]||[0,0,0];
      $('selected-name').textContent=meta.name;
      $('selected-size').textContent=`包络 ${size.x.toFixed(1)} × ${size.y.toFixed(1)} × ${size.z.toFixed(1)} mm`;
      $('part').value=id;$('part-description').textContent=meta.description;
      ['x','y','z'].forEach((a,i)=>$('offset-'+a).value=offset[i]);$('part-note').value=state.notes[id]||'';
      $('offset-status').textContent=offset.some(v=>v!==0)?'已记录位置偏移':'原始位置';
      for(const button of $('part-list').querySelectorAll('button'))button.setAttribute('aria-pressed',String(button.dataset.part===id));
    }
    function apply(){
      const guide=state.mode==='guide',step=STEPS[state.step],q=1-state.progress/100;
      for(const id of ALL){
        const g=groups[id];g.position.set(0,0,0);g.rotation.set(0,0,0);
        g.visible=guide?step.visible.includes(id):!state.hidden.includes(id);
        if(guide){
          if(state.step===0)g.position.fromArray(explodedOffset(id,.65));
          else if(step.motion==='hook'&&id==='lid'){const t=state.progress/100,a=THREE.MathUtils.degToRad(t<.4?-6:-6*(1-(t-.4)/.6)),pivot=new THREE.Vector3(0,7.2,6.0);g.rotation.x=a;g.position.copy(pivot).sub(pivot.clone().applyAxisAngle(new THREE.Vector3(1,0,0),a));g.position.y+=t<.4?-2*(1-t/.4):0;}
          else if(step.moving?.includes(id))g.position.fromArray(step.vector.map(v=>v*q));
        }else{
          g.position.fromArray(explodedOffset(id,state.explode/100));
          g.position.add(new THREE.Vector3(...(state.offsets[id]||[0,0,0])));
          if(CAPS.includes(id))g.position.z-=state.press;
          if(id==='slider')g.position.y+=state.slide;
        }
        for(const mesh of g.children){
          mesh.visible=!mesh.userData.variant||mesh.userData.variant===state.variant;
          if(id==='lid'&&state.lidMode==='off')mesh.visible=false;
          const filament=PRINTED.includes(id)?FILAMENTS[state.filaments[id]]:null;
          if(filament){mesh.material.color.set(filament.color);mesh.material.metalness=filament.metalness||.03;mesh.material.roughness=filament.opacity?.60:filament.metalness?.46:.62;}
          const shell=['front','rear'].includes(mesh.userData.type);
          mesh.material.transparent=(state.transparent&&shell)||!!filament?.opacity;
          mesh.material.opacity=(state.transparent&&shell) ? .22 : filament?.opacity||1;
          mesh.material.depthWrite=!mesh.material.transparent;
          mesh.material.emissive.setHex(id===state.selected?0x163951:0x000000);
          mesh.material.emissiveIntensity=(id===state.selected) ? .16 : 0;
        }
      }
      scene.updateMatrixWorld(true);selectionBox.setFromObject(state.selected==='front'?groups.front.children.find(m=>m.userData.variant===state.variant):groups[state.selected]);selectionBox.visible=groups[state.selected].visible&&state.labels&&groups[state.selected].children.some(m=>m.visible);
      $('scene-caption').textContent=guide?`${state.step+1} / ${STEPS.length} · ${step.title}`:state.acoustic?(state.explode===0?'音腔合拢 · 局部放大':'音腔爆炸图 · 局部放大'):(state.explode===0?'合拢状态 · 自由调整':'分解状态 · 自由调整');
      $('scene-caption').textContent=VARIANTS[state.variant].name+' · '+$('scene-caption').textContent;
      const shown=meshes.filter(m=>m.visible&&m.parent.visible).length;$('visible-count').textContent=`${shown} / ${meshes.length} 个实体可见`;
      $('explode-value').value=state.explode+'%';$('progress-value').value=Math.round(state.progress)+'%';
      $('press-value').value=state.press.toFixed(2).replace(/0$/,'')+' mm';$('slide-value').value=state.slide.toFixed(2)+' mm';
      for(const check of $('part-list').querySelectorAll('input'))check.checked=!state.hidden.includes(check.dataset.part);
      render();
    }
    function syncUI(){
      $('front-variant').value=state.variant;$('lid-mode').value=state.lidMode;$('variant-note').textContent=VARIANTS[state.variant].note;
      $('palette').value=state.palette;for(const id of PRINTED)$('color-'+id).value=state.filaments[id];
      const mats=[...new Set(PRINTED.map(id=>FILAMENTS[state.filaments[id]].material))];$('stock-note').textContent=(PALETTES[state.palette]?.note||'已选用库存内耗材。')+(mats.length>1?' PLA 与 PETG 建议分别分盘打印。':' 本方案四件均为 '+mats[0]+'。');
      const guide=state.mode==='guide';$('guide-tab').setAttribute('aria-selected',String(guide));$('free-tab').setAttribute('aria-selected',String(!guide));$('guide-panel').hidden=!guide;$('free-panel').hidden=guide;
      $('step').value=state.step;$('step-progress').value=state.progress;$('explode').value=state.explode;$('view').value=state.view;
      $('transparent').checked=state.transparent;$('labels-toggle').checked=state.labels;$('press').value=state.press;$('slide').value=state.slide;
      const step=STEPS[state.step];$('step-title').textContent=step.title;$('step-description').textContent=step.text;$('step-counter').textContent=`${state.step+1} / ${STEPS.length}`;
      $('step-checks').replaceChildren(...step.checks.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
      $('previous').disabled=state.step===0;$('next').disabled=state.step===STEPS.length-1;
      const staticStep=!step.moving;$('step-progress').disabled=staticStep;$('animate-step').disabled=staticStep;$('undo-step').disabled=staticStep;
      $('animate-step').textContent=staticStep?'查看并检查':'装入本步';$('progress-label').textContent=staticStep?'当前展示':'本步装入';
      $('step-done').checked=state.checked.includes(state.step);
      for(const b of $('step-dots').children){b.setAttribute('aria-current',Number(b.dataset.step)===state.step?'step':'false');b.classList.toggle('checked',state.checked.includes(Number(b.dataset.step)));}
      updateInspector();apply();
    }
    function select(id){state.selected=id;updateInspector();apply();save();}
    function stopAnimation(){cancelAnimationFrame(animation);animation=0;}
    function chooseStep(i){stopAnimation();state.step=i;state.progress=STEPS[i].moving?0:100;state.selected=STEPS[i].focus;state.view=STEPS[i].view;state.transparent=false;syncUI();fit();save();}
    function setMode(mode){stopAnimation();state.mode=mode;if(mode==='guide'){state.view=STEPS[state.step].view;state.selected=STEPS[state.step].focus;}syncUI();fit();save();}
    function animateStep(target){
      stopAnimation();const from=state.progress,start=performance.now(),duration=matchMedia('(prefers-reduced-motion: reduce)').matches?0:750;
      function tick(now){const t=duration?Math.min(1,(now-start)/duration):1;state.progress=from+(target-from)*(t*t*(3-2*t));$('step-progress').value=state.progress;apply();if(t<1)animation=requestAnimationFrame(tick);else{animation=0;save();}}
      animation=requestAnimationFrame(tick);
    }
    $('front-variant').onchange=e=>{state.variant=e.target.value;syncUI();fit();save();notify(VARIANTS[state.variant].note+' 玻璃周边无压边，两方案均按约1 mm胶层展示。');};
    $('lid-mode').onchange=e=>{state.lidMode=e.target.value;apply();save();};
    $('height-view').onclick=()=>{state.mode='free';state.detail=null;state.acoustic=false;state.hidden=[];state.explode=0;state.view='height';state.labels=false;syncUI();fit();save();};
    $('desk-view').onclick=()=>{state.mode='free';state.detail=null;state.acoustic=false;state.hidden=ALL.filter(id=>id!=='rear');state.explode=0;state.view='bottom';state.selected='rear';syncUI();fit();save();notify('四处矮脚高0.9 mm；声孔周围浅槽接向圆弧侧边。桌面不会直接贴住全部声孔。');};
    $('slider-closeup').onclick=()=>{state.mode='free';state.detail='slider';state.acoustic=false;state.hidden=ALL.filter(id=>!['rear','slider','pcb'].includes(id));state.explode=0;state.view='side';state.selected='slider';state.transparent=true;syncUI();fit();save();notify('内侧横边6.8→10.4 mm；槽宽减小，后盖两处弹片防脱。滑动可用右侧行程控件查看。');};
    $('palette').onchange=e=>{const p=PALETTES[e.target.value];if(!p)return;state.palette=e.target.value;state.colors={...p.colors};state.filaments={...p.filaments};syncUI();save();notify('配色：'+p.name+'。仅改变打印件颜色，静音开关和电子元件保留原色。');};
    for(const id of PRINTED)$('color-'+id).onchange=e=>{state.filaments[id]=e.target.value;state.colors[id]=FILAMENTS[e.target.value].color;state.palette='custom';syncUI();save();};
    $('guide-tab').onclick=()=>setMode('guide');$('free-tab').onclick=()=>setMode('free');
    // Native buttons remain keyboard accessible; arrow keys also switch the two tabs.
    for(const tab of [$('guide-tab'),$('free-tab')])tab.onkeydown=e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const next=tab===$('guide-tab')?$('free-tab'):$('guide-tab');next.click();next.focus();}};
    $('step').onchange=e=>chooseStep(Number(e.target.value));$('previous').onclick=()=>chooseStep(Math.max(0,state.step-1));$('next').onclick=()=>chooseStep(Math.min(STEPS.length-1,state.step+1));
    $('step-progress').oninput=e=>{stopAnimation();state.progress=Number(e.target.value);apply();};$('step-progress').onchange=save;
    $('animate-step').onclick=()=>animateStep(100);$('undo-step').onclick=()=>animateStep(0);
    $('step-done').onchange=e=>{state.checked=e.target.checked?[...new Set([...state.checked,state.step])]:state.checked.filter(n=>n!==state.step);syncUI();save();};
    $('explode').oninput=e=>{state.explode=Number(e.target.value);apply();};$('explode').onchange=()=>{fit();save();};
    $('assemble').onclick=()=>{state.explode=0;$('explode').value=0;apply();fit();save();notify('已合拢模型；保留你在自由调整中填写的位置偏移。');};
    $('part').onchange=e=>select(e.target.value);
    $('show-all').onclick=()=>{state.detail=null;state.acoustic=false;state.hidden=[];apply();fit();save();};
    $('isolate').onclick=()=>{state.hidden=ALL.filter(id=>id!==state.selected);apply();fit();save();};
    $('reset-part').onclick=()=>{state.offsets[state.selected]=[0,0,0];updateInspector();apply();save();};
    ['x','y','z'].forEach((axis,i)=>$('offset-'+axis).oninput=e=>{
      if(e.target.value===''||!e.target.validity.valid)return;
      const arr=state.offsets[state.selected]||[0,0,0];arr[i]=clamp(e.target.value,-30,30);state.offsets[state.selected]=arr;
      $('offset-status').textContent=arr.some(v=>v!==0)?'已记录位置偏移':'原始位置';apply();save();
    });
    $('part-note').oninput=e=>{state.notes[state.selected]=e.target.value;save();};
    $('press').oninput=e=>{state.press=Number(e.target.value);apply();};$('press').onchange=save;
    $('slide').oninput=e=>{state.slide=Number(e.target.value);apply();};$('slide').onchange=save;
    $('transparent').onchange=e=>{state.transparent=e.target.checked;apply();save();};$('labels-toggle').onchange=e=>{state.labels=e.target.checked;apply();save();};
    $('view').onchange=e=>{state.view=e.target.value;fit();save();};$('fit').onclick=()=>fit();
    $('slider-install').onclick=()=>{state.detail=null;state.mode='guide';chooseStep(STEPS.findIndex(s=>s.focus==='slider'));};
    $('acoustic-view').onclick=()=>{state.mode='free';state.detail=null;state.acoustic=true;state.hidden=ALL.filter(id=>!ACOUSTIC.includes(id));state.explode=65;state.selected='lid';state.view='iso';state.transparent=false;syncUI();fit();save();notify('无胶音腔：侧弹片夹住喇叭，腔盖先挂入固定钩，再扣前侧两处卡扣。盖板中央大开窗，背部保持通气。');};
    $('whole-view').onclick=()=>{state.mode='free';state.detail=null;state.acoustic=false;state.hidden=[];state.explode=65;state.selected='lid';state.view='iso';state.transparent=false;syncUI();fit();save();};
    $('rear-view').onclick=()=>{state.mode='free';state.acoustic=false;state.hidden=ALL.filter(id=>![...ACOUSTIC,'battery'].includes(id));state.explode=0;state.selected='battery';state.view='iso';state.transparent=false;syncUI();fit();save();notify('后盖内部：电池定位框 52 × 30 mm。点击“显示全部”恢复其他零件。');};
    function download(name,blob){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
    $('export').onclick=()=>{download('myMicrobyte-v08-装配调整.json',new Blob([JSON.stringify(record(),null,2)],{type:'application/json'}));notify('已导出调整记录，包含每个零件的偏移、备注和装配检查进度。');};
    $('import-button').onclick=()=>$('import-file').click();
    $('import-file').onchange=async e=>{
      const file=e.target.files[0];if(!file)return;
      try{if(file.size>1000000)throw new Error('文件超过 1 MB');const raw=JSON.parse(await file.text());if(!loadState(raw))throw new Error('请选择此页面导出的 v0.8 调整记录');stopAnimation();syncUI();fit();save();notify('已导入调整记录。');}catch(error){notify('导入失败：'+error.message);}finally{e.target.value='';}
    };
    $('screenshot').onclick=()=>{
      render();const canvas=document.createElement('canvas');canvas.width=renderer.domElement.width;canvas.height=renderer.domElement.height;const ctx=canvas.getContext('2d');ctx.fillStyle=getComputedStyle($('stage')).backgroundColor;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(renderer.domElement,0,0);const ratio=renderer.getPixelRatio();ctx.fillStyle=getComputedStyle(root).color;ctx.font=`${14*ratio}px sans-serif`;ctx.fillText('myMicrobyte v0.8 · '+$('scene-caption').textContent+' · '+(PALETTES[state.palette]?.name||'自定义配色'),18*ratio,28*ratio);canvas.toBlob(blob=>{if(blob)download('myMicrobyte-v08-装配视图.png',blob);});notify('已保存当前 3D 视图 PNG。偏移量与备注可用“导出调整记录”保存。');
    };
    const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2();let down=null;
    renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
    renderer.domElement.addEventListener('pointerup',e=>{
      if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;down=null;
      const r=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(mouse,camera);
      const hits=raycaster.intersectObjects(meshes.filter(m=>m.visible&&m.parent.visible),false);
      // In transparent mode, prioritize the internal part behind the shell.
      const hit=state.transparent?(hits.find(h=>!['front','rear'].includes(h.object.userData.id))||hits[0]):hits[0];if(hit)select(hit.object.userData.id);
    });
    controls.addEventListener('change',render);
    new ResizeObserver(()=>{resize();fit();}).observe(host);
    resize();syncUI();fit();$('loading').hidden=true;
    renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();$('loading').hidden=false;$('loading').textContent='3D 显示已暂停，请刷新页面恢复；已保存的调整记录会保留。';});
    // Preserve meaningful edits without changing the original FreeCAD or print files.
  } catch(error) {
    $('loading').setAttribute('role','alert');$('loading').textContent='3D 模型未能加载：'+error.message+'。请使用支持 WebGL 的新版 Chrome、Edge 或 Safari 打开本页。';
  }
})();
