(async function () {
  'use strict';
  const root = document.getElementById('assembly-workbench');
  const $ = id => root.querySelector('#' + id);
  const STORAGE = 'myMicrobyte-v05-assembly-guide-v1';
  const CAP_NAMES = [];
  const CAPS = CAP_NAMES.map(n => 'Button_' + n);
  const UPPER = ['front','inserts'];
  const ALL = ['front','rear',...CAPS,'pcb','slider','battery','speaker','inserts','screws'];
  const META = {
    front: {name:'前盖', description:'按键区降低 0.9 mm，裸开关预计露出 1.6 mm；十字开口去掉易断中心片。屏幕下陷约 1.8 mm，内侧短定位框仅伸出 0.75 mm，TF 侧增加遮板唇边。'},
    rear: {name:'后盖', description:'电池框净空增至 52 × 30 mm，底厚 1.4 mm。拨帽导轨向上敞开，由前盖封住上方。保留 R1.8 外缘圆角、喇叭座和充电灯孔。'},
    pcb: {name:'PCB 与屏幕', description:'PCB 支承高度仍为 9 mm；上方夹持空间由 1.75 增至 2.15 mm。玻璃让位名义 0.70 mm，检查包络最小 0.50 mm。实物板翘曲及焊锡高度仍需试装。'},
    slider: {name:'电源拨帽', description:'先放 PCB，再从后盖上方落入导轨，开口叉槽套住拨杆，最后盖前盖。机械活动范围 3.6 mm；5 条圆边防滑筋，打印时纹路朝上。电气两档需实物确认。'},
    battery: {name:'3 mm 电池占位', description:'型号未定。图中 50 × 28 × 3 mm，比上一版加宽 3 mm。成品含保护板和包边建议 ≤51 × 29 × 3.3 mm，底部另留 0.3 mm 胶层；距 ESP32 约 0.68 mm。'},
    speaker: {name:'1510 喇叭', description:'15 × 10 × 3.5 mm，发声面朝后盖。位置保留，电池扩大后仍避开喇叭、电池端子和插头。'},
    inserts: {name:'热熔螺母 ×4', description:'M2×2×3，前盖预孔 Ø2.8 mm。将螺母装平并冷却，避免凸出柱底顶住 PCB。'},
    screws: {name:'M2×5 螺丝 ×4', description:'仍用 M2×5，名义螺纹啮合约 1.75 mm。先确认有 PCB 时壳体可自然合拢，再轻拧螺丝。'}
  };
  const STEPS = [
    {title:'检查新版三件打印件', text:'前盖、后盖与拨帽。九个按键继续使用原装静音开关。', checks:['十字键为有意连通的开口，没有需要剪除的中心片。','清理底边、拨帽导轨及叉槽的支撑和毛边。'], visible:ALL, focus:'front', view:'iso'},
    {title:'先装热熔螺母', text:'将四个 M2×2×3 螺母装入前盖柱孔，放平冷却。', checks:['螺母端面与柱底齐平，不顶出。','本次 PCB 上方多留 0.4 mm，不依靠螺丝强压板子。'], visible:['front','inserts'], moving:['inserts'], vector:[0,0,-12], focus:'inserts', view:'inside'},
    {title:'放置电池与喇叭', text:'在后盖固定 3 mm 薄电池和喇叭，线束避开柱孔与导轨。', checks:['电池框净空 52 × 30 mm，成品电池建议 ≤51 × 29 × 3.3 mm。','喇叭朝后盖出声；胶水只粘边缘，避开振膜。'], visible:['rear','battery','speaker'], moving:['battery','speaker'], vector:[0,0,17], focus:'battery', view:'iso'},
    {title:'将 PCB 放入后盖', text:'屏幕面朝上，让 PCB 四角安装孔对齐后盖支柱。', checks:['底部元件和插头不能压住电池或喇叭。','先不放前盖，确认 PCB 平稳落在四个支柱上。'], visible:['rear','battery','speaker','pcb'], moving:['pcb'], vector:[0,0,24], focus:'pcb', view:'iso'},
    {title:'从上方装入拨帽', text:'拨帽纹路朝外，沿敞口导轨垂直落下，贯通叉槽套住白色拨杆。', checks:['后盖横杠已移到前盖，无需剪断外壳。','套入后轻推两个档位，不能让塑料止挡提前挡住拨杆。'], visible:['rear','pcb','slider'], moving:['slider'], vector:[0,0,12], focus:'slider', view:'side'},
    {title:'合拢前盖', text:'对准屏幕、九个开关与 TF 遮板唇边，将前盖轻放到位。前盖同时封住拨帽导轨上方。', checks:['设计接缝仍为 0.1 mm；有明显缝隙时先找接触点。','按钮预计露出约 1.6 mm；玻璃不得受压，TF 卡应顺畅插入。'], visible:ALL.filter(id=>id!=='screws'), moving:UPPER, vector:[0,0,30], focus:'front', view:'iso'},
    {title:'装入四颗螺丝', text:'从后盖装入 M2×5，先轻带上，再交叉、均匀拧紧。', checks:['螺纹名义啮合约 1.75 mm。','如 PCB 有轻微晃动，可在支承位置加薄绝缘垫；不要垫压屏幕或电池。'], visible:ALL, moving:['screws'], vector:[0,0,-15], focus:'screws', view:'bottom'},
    {title:'完成实物检查', text:'重点检查合缝、按键触感、屏幕深度、TF 插拔及两档电源。', checks:['前盖左下角 RUN 孔已封闭；检查后盖充电灯的可见性。','拨帽动画展示机械范围，不模拟电触点。','可以在自由调整中选中零件，填写偏移和备注，再导出记录。'], visible:ALL, focus:'front', view:'iso'}
  ];
  const state = {mode:'free', step:0, progress:100, explode:65, selected:'front', transparent:false, labels:true, view:'iso', press:0, slide:0, hidden:[], offsets:{}, notes:{}, checked:[]};
  const clamp = (v,min,max,fallback=0) => Number.isFinite(Number(v)) ? Math.max(min,Math.min(max,Number(v))) : fallback;
  function loadState(raw) {
    if (!raw || raw.schema !== 'myMicrobyte.assembly.v1' || raw.model !== 'v0.5') return false;
    const s=raw.state;
    if (!s || typeof s!=='object') return false;
    state.mode=s.mode==='guide'?'guide':'free'; state.step=Math.round(clamp(s.step,0,STEPS.length-1));
    state.progress=clamp(s.progress,0,100,100); state.explode=clamp(s.explode,0,100,35);
    state.selected=ALL.includes(s.selected)?s.selected:'front';
    state.transparent=!!s.transparent;state.labels=s.labels!==false;
    state.view=['iso','top','inside','bottom','side','tf'].includes(s.view)?s.view:'iso';
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
  const record = () => ({schema:'myMicrobyte.assembly.v1', model:'v0.5', savedAt:new Date().toISOString(), units:'mm', coordinates:'Original CAD world axes: X long side, Y short side, Z thickness. Translation only; no CAD rebuild or collision check.', state, adjustments:ALL.filter(id=>state.notes[id]||state.offsets[id]?.some(v=>v!==0)).map(id=>({part:id,name:META[id].name,translationMm:state.offsets[id]||[0,0,0],note:state.notes[id]||''}))});
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
    const directions={iso:[90,-120,112],top:[0,-.001,1],inside:[55,-65,-120],bottom:[55,-75,-115],side:[140,-14,30],tf:[0,150,24]};
    function fit(view=state.view){
      const box=(state.mode==='guide'&&state.step===4?new THREE.Box3(new THREE.Vector3(34,-13,4),new THREE.Vector3(46,2,25)):currentBox()),center=box.getCenter(new THREE.Vector3()),dir=new THREE.Vector3(...directions[view]).normalize();
      controls.target.copy(center);camera.position.copy(center).add(dir);camera.lookAt(center);camera.updateMatrixWorld();
      const inverse=camera.matrixWorldInverse.clone(),tan=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
      let distance=30;
      for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
        const v=new THREE.Vector3(x,y,z).applyMatrix4(inverse);distance=Math.max(distance,Math.abs(v.y)/tan+v.z+1,Math.abs(v.x)/(tan*camera.aspect)+v.z+1);
      }
      camera.position.copy(center).addScaledVector(dir,distance*1.10);controls.update();render();
    }
    function explodedOffset(id,e){
      return [id==='slider'?e*17:0,0,e*(id==='front'||id==='inserts'?52:CAPS.includes(id)?35:id==='pcb'?18:['battery','speaker'].includes(id)?6:id==='screws'?-24:0)];
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
    $('step').onchange=e=>chooseStep(Number(e.target.value));$('previous').onclick=()=>chooseStep(Math.max(0,state.step-1));$('next').onclick=()=>chooseStep(Math.min(STEPS.length-1,state.step+1));
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
    $('slider-install').onclick=()=>{state.mode='guide';chooseStep(4);};
    $('rear-view').onclick=()=>{state.mode='free';state.hidden=ALL.filter(id=>!['rear','battery','speaker'].includes(id));state.explode=0;state.selected='battery';state.view='iso';state.transparent=false;syncUI();fit();save();notify('后盖内部：电池定位框 52 × 30 mm。点击“显示全部”恢复其他零件。');};
    function download(name,blob){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
    $('export').onclick=()=>{download('myMicrobyte-v05-装配调整.json',new Blob([JSON.stringify(record(),null,2)],{type:'application/json'}));notify('已导出调整记录，包含每个零件的偏移、备注和装配检查进度。');};
    $('import-button').onclick=()=>$('import-file').click();
    $('import-file').onchange=async e=>{
      const file=e.target.files[0];if(!file)return;
      try{if(file.size>1000000)throw new Error('文件超过 1 MB');const raw=JSON.parse(await file.text());if(!loadState(raw))throw new Error('请选择此页面导出的 v0.5 调整记录');stopAnimation();syncUI();fit();save();notify('已导入调整记录。');}catch(error){notify('导入失败：'+error.message);}finally{e.target.value='';}
    };
    $('screenshot').onclick=()=>{
      render();const canvas=document.createElement('canvas');canvas.width=renderer.domElement.width;canvas.height=renderer.domElement.height;const ctx=canvas.getContext('2d');ctx.fillStyle=getComputedStyle($('stage')).backgroundColor;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(renderer.domElement,0,0);const ratio=renderer.getPixelRatio();ctx.fillStyle=getComputedStyle(root).color;ctx.font=`${14*ratio}px sans-serif`;ctx.fillText('myMicrobyte v0.5 · '+$('scene-caption').textContent,18*ratio,28*ratio);canvas.toBlob(blob=>{if(blob)download('myMicrobyte-v05-装配视图.png',blob);});notify('已保存当前 3D 视图 PNG。偏移量与备注可用“导出调整记录”保存。');
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
