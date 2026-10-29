(async function () {
  'use strict';
  const root = document.getElementById('assembly-workbench');
  const $ = id => root.querySelector('#' + id);
  const STORAGE = 'myMicrobyte-v03-assembly-guide-v1';
  const CAP_NAMES = ['UP','DOWN','LEFT','RIGHT','START','SELECT','MENU','A','B'];
  const CAPS = CAP_NAMES.map(n => 'Button_' + n);
  const UPPER = ['front','inserts',...CAPS,'pcb','slider'];
  const ALL = ['front','rear',...CAPS,'pcb','slider','battery','speaker','inserts','screws'];
  const META = {
    front: {name:'前盖', description:'浅屏幕窗口、九个按键导槽与四个热熔孔。先从内侧装螺母和按键，再放 PCB。'},
    rear: {name:'后盖', description:'底板 1.6 mm；电池定位框净空 57 × 37 mm。Type-C 与 TF 开口位于侧边。'},
    pcb: {name:'PCB 与板载元件', description:'PCB、屏幕和板载元件整体移动，保持焊接位置。屏幕按 1.9 mm + 0.1 mm 胶层参考。'},
    slider: {name:'电源拨帽', description:'内叉槽 1.8 × 1.5 mm，套住 MSK-12C02 白色拨杆。前后盖合拢后捕获定位。'},
    battery: {name:'503550 电池', description:'标称 50 × 35 × 5 mm，底部预留 0.3 mm 胶层。框内 57 × 37 mm；建议成品不超过 56 × 36 × 5 mm。'},
    speaker: {name:'1510 喇叭', description:'15 × 10 × 3.5 mm，放入靠近 TF 侧的定位槽，发声面朝后盖。'},
    inserts: {name:'热熔螺母 ×4', description:'M2×2×3：外径 3 mm、长度 2 mm。前盖预孔 Ø2.8 mm、深 2.15 mm；从 PCB 侧装入。'},
    screws: {name:'M2×5 螺丝 ×4', description:'从后盖四个深沉孔装入，穿过 PCB 后旋入前盖螺母。此版本使用 M2×5。'}
  };
  for (const n of CAP_NAMES) META['Button_'+n] = {name:n+' 按键帽', description:'两侧长条定位耳沿前盖导槽装入。初始触头间隙约 0.03 mm；帽顶高出面板 1.8 mm。'};
  const STEPS = [
    {title:'清理打印件', short:'清理', text:'准备前后盖、九个按键帽和电源拨帽，共 12 件打印件。清掉支撑和毛边，再开始试装。', checks:['重点清理屏幕下沉区、按键耳槽、拨帽叉槽和螺丝沉孔。','先让按键耳槽、拨帽导轨能顺畅滑动。'], visible:ALL, focus:'front', view:'iso'},
    {title:'热熔四个螺母', short:'螺母', text:'将前盖内侧朝上，把四个 M2×2×3 螺母从 PCB 一侧装入柱孔。模型下方是前盖内侧。', checks:['保持螺母与柱孔同轴，不要压穿前盖。','螺母冷却、位置稳定后再放入 PCB。'], visible:['front','inserts'], moving:['inserts'], vector:[0,0,-12], focus:'inserts', view:'inside'},
    {title:'装入九个按键帽', short:'按键', text:'从前盖内侧装入各按键。两根定位耳对准各自的导槽，手指接触面朝外。', checks:['定位耳沿导槽移动；不要把 PLA 定位耳硬掰成卡扣。','暂时托住按键，稍后用 PCB 限制按键脱出。'], visible:['front','inserts',...CAPS], moving:CAPS, vector:[0,0,-16], focus:'Button_UP', view:'inside'},
    {title:'对准并放入 PCB', short:'PCB', text:'托住前盖与按键，把 PCB 的屏幕面朝向前盖，四角孔对准定位柱。', checks:['屏幕对齐窗口；九个按键触头分别对准开关。','逐个试按，确认能回弹，再继续合盖。'], visible:['front','inserts',...CAPS,'pcb'], moving:['pcb'], vector:[0,0,-24], focus:'pcb', view:'inside'},
    {title:'套入电源拨帽', short:'拨帽', text:'将侧边拨帽的内叉槽套在白色拨杆上。拨帽最终由闭合后的前后盖捕获。', checks:['叉槽确实套住拨杆，不能顶住开关本体。','轻推到两个电气档位，确认没有被外壳提前挡住。'], visible:UPPER, moving:['slider'], vector:[16,0,0], focus:'slider', view:'side'},
    {title:'放入喇叭与电池', short:'后盖', text:'在后盖内放入喇叭和 503550 电池。喇叭朝后发声，电池放在矩形定位框内。', checks:['检查电池实际包边、保护板和插头尺寸。','留出 PCB 电池端子和喇叭端子的空间；走线避开柱孔和止口。'], visible:['rear','battery','speaker'], moving:['battery','speaker'], vector:[0,0,17], focus:'battery', view:'iso'},
    {title:'对齐前后盖', short:'合盖', text:'连接并理好线，将前盖、按键、PCB 和拨帽组件对准后盖，沿厚度方向轻轻合拢。', checks:['检查拨帽进入侧边导轨，Type-C 和 TF 对准开口。','接缝应自然贴合；遇到阻力先查干涉和夹线。'], visible:ALL.filter(id=>id!=='screws'), moving:UPPER, vector:[0,0,30], focus:'front', view:'iso'},
    {title:'装入四颗螺丝', short:'螺丝', text:'从后盖装入四颗 M2×5 螺丝，先轻带上，再对角、均匀拧紧。', checks:['不要用螺丝强拉未对齐的前后盖。','该沉孔结构使用 M2×5，不能直接换成 M2×10。'], visible:ALL, moving:['screws'], vector:[0,0,-15], focus:'screws', view:'bottom'},
    {title:'完成试装检查', short:'检查', text:'逐一检查九个按键、电源拨帽、Type-C、TF 和壳体接缝。发现问题后切换自由调整，记录对应零件。', checks:['九键回弹顺畅，电源两档可到位。','Type-C 插头与 TF 卡能正常插拔。','接缝贴合，屏幕无受压，壳内没有松动件。'], visible:ALL, focus:'front', view:'iso'}
  ];
  const state = {mode:'guide', step:0, progress:100, explode:35, selected:'front', transparent:false, labels:true, view:'iso', press:0, slide:0, hidden:[], offsets:{}, notes:{}, checked:[]};
  const clamp = (v,min,max,fallback=0) => Number.isFinite(Number(v)) ? Math.max(min,Math.min(max,Number(v))) : fallback;
  function loadState(raw) {
    if (!raw || raw.schema !== 'myMicrobyte.assembly.v1' || raw.model !== 'v0.3') return false;
    const s=raw.state;
    if (!s || typeof s!=='object') return false;
    state.mode=s.mode==='guide'?'guide':'free'; state.step=Math.round(clamp(s.step,0,8));
    state.progress=clamp(s.progress,0,100,100); state.explode=clamp(s.explode,0,100,35);
    state.selected=ALL.includes(s.selected)?s.selected:'front';
    state.transparent=!!s.transparent;state.labels=s.labels!==false;
    state.view=['iso','top','inside','bottom','side'].includes(s.view)?s.view:'iso';
    state.press=clamp(s.press,0,.6);state.slide=clamp(s.slide,0,1.8);
    state.hidden=Array.isArray(s.hidden)?s.hidden.filter(id=>ALL.includes(id)):[];
    state.checked=Array.isArray(s.checked)?s.checked.filter(n=>Number.isInteger(n)&&n>=0&&n<=8):[];
    state.offsets={};state.notes={};
    for(const id of ALL){
      if(Array.isArray(s.offsets?.[id])&&s.offsets[id].length===3)state.offsets[id]=s.offsets[id].map(v=>clamp(v,-30,30));
      if(typeof s.notes?.[id]==='string')state.notes[id]=s.notes[id].slice(0,1000);
    }
    return true;
  }
  try{loadState(JSON.parse(localStorage.getItem(STORAGE)));}catch(e){}
  const record = () => ({schema:'myMicrobyte.assembly.v1', model:'v0.3', savedAt:new Date().toISOString(), units:'mm', coordinates:'Original CAD world axes: X long side, Y short side, Z thickness. Translation only; no CAD rebuild or collision check.', state, adjustments:ALL.filter(id=>state.notes[id]||state.offsets[id]?.some(v=>v!==0)).map(id=>({part:id,name:META[id].name,translationMm:state.offsets[id]||[0,0,0],note:state.notes[id]||''}))});
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
    renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;
    renderer.domElement.setAttribute('aria-label','myMicrobyte 3D 装配模型');host.appendChild(renderer.domElement);
    controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=12;controls.maxDistance=650;
    scene.add(new THREE.AmbientLight(0xffffff,2.1));
    for(const [pos,intensity] of [[[-75,-95,145],3.4],[[90,80,50],2.2],[[0,0,-100],1.8]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...pos);scene.add(light);}
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
      const mesh=new THREE.Mesh(geo,material);mesh.userData={id:classify(item),type:item.type,name:item.name};groups[mesh.userData.id].add(mesh);meshes.push(mesh);
    }
    for(const id of ALL){
      const box=new THREE.Box3().setFromObject(groups[id]);groups[id].userData={box,center:box.getCenter(new THREE.Vector3()),size:box.getSize(new THREE.Vector3())};
      if(['front','rear','pcb','battery','speaker','slider'].includes(id)){
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
        if(!state.labels||!g.visible){el.hidden=true;continue;}
        const p=g.userData.center.clone().add(g.position).project(camera);
        const x=(p.x+1)/2*host.clientWidth,y=(-p.y+1)/2*host.clientHeight;
        const hidden=p.z>1||p.z< -1||x<65||x>host.clientWidth-65||y<58||y>host.clientHeight-45||occupied.some(([px,py])=>Math.abs(px-x)<115&&Math.abs(py-y)<30);
        el.hidden=hidden;if(hidden)continue;
        occupied.push([x,y]);el.style.left=x+'px';el.style.top=y+'px';el.classList.toggle('selected',id===state.selected);
      }
    }
    function render(){if(!renderer)return;renderer.render(scene,camera);renderLabels();}
    function resize(){const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render();}
    function currentBox(){const box=new THREE.Box3();scene.updateMatrixWorld(true);for(const id of ALL)if(groups[id].visible)box.union(new THREE.Box3().setFromObject(groups[id]));return box.isEmpty()?groups.front.userData.box.clone():box;}
    const directions={iso:[90,-120,112],top:[0,-.001,1],inside:[55,-65,-120],bottom:[55,-75,-115],side:[140,-14,30]};
    function fit(view=state.view){
      const box=currentBox(),center=box.getCenter(new THREE.Vector3()),dir=new THREE.Vector3(...directions[view]).normalize();
      controls.target.copy(center);camera.position.copy(center).add(dir);camera.lookAt(center);camera.updateMatrixWorld();
      const inverse=camera.matrixWorldInverse.clone(),tan=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
      let distance=30;
      for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
        const v=new THREE.Vector3(x,y,z).applyMatrix4(inverse);distance=Math.max(distance,Math.abs(v.y)/tan+v.z+1,Math.abs(v.x)/(tan*camera.aspect)+v.z+1);
      }
      camera.position.copy(center).addScaledVector(dir,distance*1.26);controls.update();render();
    }
    function explodedOffset(id,e){
      return [id==='slider'?e*17:0,0,e*(id==='front'||id==='inserts'?52:CAPS.includes(id)?35:id==='pcb'?18:['battery','speaker'].includes(id)?6:id==='screws'?-12:0)];
    }
    function updateInspector(){
      const id=state.selected,meta=META[id],size=groups[id].userData.size,offset=state.offsets[id]||[0,0,0];
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
        const g=groups[id];g.position.set(0,0,0);
        g.visible=guide?step.visible.includes(id):!state.hidden.includes(id);
        if(guide){
          if(state.step===0)g.position.fromArray(explodedOffset(id,.65));
          else if(step.moving?.includes(id))g.position.fromArray(step.vector.map(v=>v*q));
        }else{
          g.position.fromArray(explodedOffset(id,state.explode/100));
          g.position.add(new THREE.Vector3(...(state.offsets[id]||[0,0,0])));
          if(CAPS.includes(id))g.position.z-=state.press;
          if(id==='slider')g.position.y+=state.slide;
        }
        for(const mesh of g.children){
          const shell=['front','rear'].includes(mesh.userData.type);
          mesh.material.transparent=state.transparent&&shell;
          mesh.material.opacity=(state.transparent&&shell) ? .22 : 1;
          mesh.material.depthWrite=!(state.transparent&&shell);
          mesh.material.emissive.setHex(id===state.selected?0x163951:0x000000);
          mesh.material.emissiveIntensity=(id===state.selected) ? .16 : 0;
        }
      }
      scene.updateMatrixWorld(true);selectionBox.setFromObject(groups[state.selected]);selectionBox.visible=groups[state.selected].visible;
      $('scene-caption').textContent=guide?`${state.step+1} / ${STEPS.length} · ${step.title}`:state.explode===0?'合拢状态 · 自由调整':'分解状态 · 自由调整';
      const shown=meshes.filter(m=>m.parent.visible).length;$('visible-count').textContent=`${shown} / ${meshes.length} 个实体可见`;
      $('explode-value').value=state.explode+'%';$('progress-value').value=Math.round(state.progress)+'%';
      $('press-value').value=state.press.toFixed(2).replace(/0$/,'')+' mm';$('slide-value').value=state.slide.toFixed(1)+' mm';
      for(const check of $('part-list').querySelectorAll('input'))check.checked=!state.hidden.includes(check.dataset.part);
      render();
    }
    function syncUI(){
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
    $('guide-tab').onclick=()=>setMode('guide');$('free-tab').onclick=()=>setMode('free');
    // Native buttons remain keyboard accessible; arrow keys also switch the two tabs.
    for(const tab of [$('guide-tab'),$('free-tab')])tab.onkeydown=e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const next=tab===$('guide-tab')?$('free-tab'):$('guide-tab');next.click();next.focus();}};
    $('step').onchange=e=>chooseStep(Number(e.target.value));$('previous').onclick=()=>chooseStep(Math.max(0,state.step-1));$('next').onclick=()=>chooseStep(Math.min(8,state.step+1));
    $('step-progress').oninput=e=>{stopAnimation();state.progress=Number(e.target.value);apply();};$('step-progress').onchange=save;
    $('animate-step').onclick=()=>animateStep(100);$('undo-step').onclick=()=>animateStep(0);
    $('step-done').onchange=e=>{state.checked=e.target.checked?[...new Set([...state.checked,state.step])]:state.checked.filter(n=>n!==state.step);syncUI();save();};
    $('explode').oninput=e=>{state.explode=Number(e.target.value);apply();};$('explode').onchange=()=>{fit();save();};
    $('assemble').onclick=()=>{state.explode=0;$('explode').value=0;apply();fit();save();notify('已合拢模型；保留你在自由调整中填写的位置偏移。');};
    $('part').onchange=e=>select(e.target.value);
    $('show-all').onclick=()=>{state.hidden=[];apply();fit();save();};
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
    $('rear-view').onclick=()=>{state.mode='free';state.hidden=ALL.filter(id=>!['rear','battery','speaker'].includes(id));state.explode=0;state.selected='battery';state.view='iso';state.transparent=false;syncUI();fit();save();notify('后盖内部：电池定位框 57 × 37 mm。点击“显示全部”恢复其他零件。');};
    function download(name,blob){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
    $('export').onclick=()=>{download('myMicrobyte-v03-装配调整.json',new Blob([JSON.stringify(record(),null,2)],{type:'application/json'}));notify('已导出调整记录，包含每个零件的偏移、备注和装配检查进度。');};
    $('import-button').onclick=()=>$('import-file').click();
    $('import-file').onchange=async e=>{
      const file=e.target.files[0];if(!file)return;
      try{if(file.size>1000000)throw new Error('文件超过 1 MB');const raw=JSON.parse(await file.text());if(!loadState(raw))throw new Error('请选择此页面导出的 v0.3 调整记录');stopAnimation();syncUI();fit();save();notify('已导入调整记录。');}catch(error){notify('导入失败：'+error.message);}finally{e.target.value='';}
    };
    $('screenshot').onclick=()=>{
      render();const canvas=document.createElement('canvas');canvas.width=renderer.domElement.width;canvas.height=renderer.domElement.height;const ctx=canvas.getContext('2d');ctx.fillStyle=getComputedStyle($('stage')).backgroundColor;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(renderer.domElement,0,0);const ratio=renderer.getPixelRatio();ctx.fillStyle=getComputedStyle(root).color;ctx.font=`${14*ratio}px sans-serif`;ctx.fillText('myMicrobyte v0.3 · '+$('scene-caption').textContent,18*ratio,28*ratio);canvas.toBlob(blob=>{if(blob)download('myMicrobyte-v03-装配视图.png',blob);});notify('已保存当前 3D 视图 PNG。偏移量与备注可用“导出调整记录”保存。');
    };
    const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2();let down=null;
    renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
    renderer.domElement.addEventListener('pointerup',e=>{
      if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;down=null;
      const r=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(mouse,camera);
      const hits=raycaster.intersectObjects(meshes.filter(m=>m.parent.visible),false);
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
