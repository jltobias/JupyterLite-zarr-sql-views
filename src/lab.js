import {Deck,MapView,OrbitView,COORDINATE_SYSTEM} from '@deck.gl/core';
import {GeoJsonLayer,PolygonLayer,PointCloudLayer,LineLayer,TextLayer} from '@deck.gl/layers';
import {openEngine} from './engine.js';
import {timeSummary,geojson} from './model.js';
import {color,gradient} from './upstream-colors.ts';

const $=id=>document.getElementById(id);
const base=new URL('../data/',document.baseURI);
let meta,rows=[],deck,engine,catalog,boundaries,point=null,timer=null,busy=false;
const params=new URLSearchParams(location.search);
const timeSpacing=()=>Math.max(meta.shape[1],meta.shape[2])*.7/Math.max(1,meta.shape[0]-1);
function status(message,error=false){$('status').textContent=message;$('status').classList.toggle('error',error);}
function lock(value){busy=value;for(const id of ['dataset','query','export','play'])$(id).disabled=value;}
function stop(){clearInterval(timer);timer=null;$('play').textContent='▶ Play time';}
function viewState(){
  const mode=$('mode').value, [nt,ny,nx]=meta.shape;
  const height=mode==='cube'?(nt-1)*timeSpacing():12;
  if(['cube','scene'].includes(mode)) return {target:[nx/2,ny/2,height/2],rotationX:30,rotationOrbit:-25,
    zoom:Math.log2(Math.min($('map').clientWidth,$('map').clientHeight)*.85/Math.hypot(nx,ny,height)),minZoom:-2,maxZoom:8};
  const span=Math.max(Math.abs(meta.lon.at(-1)-meta.lon[0]),Math.abs(meta.lat.at(-1)-meta.lat[0]));
  return {longitude:(meta.lon[0]+meta.lon.at(-1))/2,latitude:(meta.lat[0]+meta.lat.at(-1))/2,zoom:Math.log2(260/span),pitch:mode==='columns'?48:0,bearing:mode==='columns'?-20:0};
}
function resetView(){deck?.setProps({initialViewState:viewState()});}
function render(reset=false){
  if(!meta||!deck)return;
  const mode=$('mode').value,t=Number($('time').value),isOrbit=['cube','scene'].includes(mode);
  const visible=mode==='cube'?rows:rows.filter(r=>r.t===t);
  const [lo,hi]=meta.range;
  const colors=r=>{const c=color(r.value,lo,hi,meta.palette);if(mode==='cube'&&r.t!==t)c[3]=95;return c;};
  let layers=[];
  if(!isOrbit){
    layers.push(new GeoJsonLayer({id:'land',data:boundaries,filled:true,stroked:true,getFillColor:[22,44,51],getLineColor:[72,102,109],lineWidthMinPixels:0.6}));
    const dx=Math.abs(meta.lon[1]-meta.lon[0])/2,dy=Math.abs(meta.lat[1]-meta.lat[0])/2;
    layers.push(new PolygonLayer({id:'grid-'+mode,data:visible,getPolygon:r=>[[r.lon-dx,r.lat-dy],[r.lon+dx,r.lat-dy],[r.lon+dx,r.lat+dy],[r.lon-dx,r.lat+dy]],
      getFillColor:colors,extruded:mode==='columns',getElevation:r=>(r.value-lo)/(hi-lo||1)*Math.abs(meta.lon.at(-1)-meta.lon[0])*6500,
      opacity:0.88,pickable:true,updateTriggers:{getFillColor:[meta.id],getElevation:[meta.id]}}));
  }else{
    const coords=r=>[r.col,meta.shape[1]-1-r.row,mode==='cube'?r.t*timeSpacing():(r.value-lo)/(hi-lo||1)*12];
    layers.push(new PointCloudLayer({id:'cube-'+mode,data:visible,coordinateSystem:COORDINATE_SYSTEM.CARTESIAN,getPosition:coords,getColor:colors,
      pointSize:mode==='cube'?3:7,sizeUnits:'pixels',pickable:true,opacity:0.88,updateTriggers:{getPosition:[mode,meta.id],getColor:[meta.id,t]}}));
    const nx=meta.shape[2],ny=meta.shape[1],height=mode==='cube'?Math.max(3,(meta.shape[0]-1)*timeSpacing()):12;
    layers.push(new LineLayer({id:'axes',coordinateSystem:COORDINATE_SYSTEM.CARTESIAN,data:[{s:[0,0,0],e:[nx,0,0]},{s:[0,0,0],e:[0,ny,0]},{s:[0,0,0],e:[0,0,height]}],getSourcePosition:r=>r.s,getTargetPosition:r=>r.e,getColor:[175,205,207],getWidth:1.5}));
    layers.push(new TextLayer({id:'axis-labels',coordinateSystem:COORDINATE_SYSTEM.CARTESIAN,data:[{p:[nx+2,0,0],s:'longitude →'},{p:[0,ny+2,0],s:'latitude →'},{p:[0,0,height+2],s:mode==='cube'?'time index ↑':'value ↑ (scaled)'}],getPosition:r=>r.p,getText:r=>r.s,getColor:[230,242,239],getSize:12,billboard:true}));
  }
  deck.setProps({views:isOrbit?new OrbitView({orbitAxis:'Z'}):new MapView({repeat:false}),...(reset?{initialViewState:viewState()}:{}),layers,
    getTooltip:({object:r})=>r&&Number.isFinite(r.value)?{text:`${meta.times[r.t]} | ${r.lon.toFixed(3)}, ${r.lat.toFixed(3)}\n${r.value.toFixed(3)} ${meta.units}\n${meta.kind.toUpperCase()}`} : null,
    onClick:({object:r})=>{if(r&&Number.isFinite(r.value)){point={row:r.row,col:r.col};render();}}});
  $('time-label').textContent=meta.times[t];$('count').textContent=rows.length.toLocaleString();$('visible').textContent=visible.length.toLocaleString();
  $('map-note').textContent=isOrbit?'Drag to orbit · scroll to zoom · vertical axis '+(mode==='cube'?'is time index, not elevation':'is scaled value, not a surveyed surface'):'Drag to pan · scroll to zoom · click a cell for its time series';
  $('table').replaceChildren(...visible.slice(0,100).map(r=>{
    const tr=document.createElement('tr');for(const val of [meta.times[r.t],r.lon.toFixed(4),r.lat.toFixed(4),r.value.toFixed(4)]){const td=document.createElement('td');td.textContent=val;tr.append(td);}return tr;
  }));
  chart(point?rows.filter(r=>r.row===point.row&&r.col===point.col):rows);
}
function chart(data){
  $('chart-title').textContent=point?`Cell (${point.row}, ${point.col}) through time`:'Selected-cell mean through time';
  const summary=timeSummary(data,meta.times),[lo,hi]=meta.range;
  const x=t=>50+t*700/Math.max(1,summary.length-1),y=v=>110-(v-lo)/(hi-lo||1)*85;
  // Labels originate only from our checked-in catalog. User SQL is never rendered as HTML.
  let s=`<path d="M50 15V115H760" fill="none" stroke="#54717b"/><text x="3" y="20">${hi.toFixed(1)}</text><text x="3" y="115">${lo.toFixed(1)}</text>`;
  for(let i=0;i<summary.length;i++){
    const a=summary[i],prev=summary[i-1];
    if(a.mean!==null){if(prev?.mean!==null&&prev)s+=`<line x1="${x(i-1)}" y1="${y(prev.mean)}" x2="${x(i)}" y2="${y(a.mean)}" stroke="#a3e6c6" stroke-width="2"/>`;s+=`<circle cx="${x(i)}" cy="${y(a.mean)}" r="4" fill="#e3c47a"><title>${a.label}: ${a.mean.toFixed(3)}; n=${a.n}</title></circle>`;}
    if(i===0||i===summary.length-1||summary.length<=4)s+=`<text x="${x(i)}" y="140" text-anchor="middle">${a.label}</text>`;
  }
  if(!data.length)s+='<text x="350" y="70">No matching cells</text>';
  $('chart').innerHTML=s;
}
async function query(){
  if(busy)return;lock(true);stop();status('Querying local cells…');
  try{const result=await engine.filter($('predicate').value);rows=result;point=null;render();status('Ready · query applied');}
  catch(e){status('Query rejected: '+e.message+' Previous selection retained.',true);}
  finally{lock(false);}
}
async function load(){
  lock(true);stop();status('Reading Zarr chunks…');let loaded=false;
  try{
    meta=catalog.find(d=>d.id===$('dataset').value);await engine.load(meta,base);
    $('time').max=meta.times.length-1;$('time').value=0;point=null;
    $('description').textContent=meta.description;$('kind').textContent=meta.kind==='observed'?'OBSERVATIONS · TEACHING EXTRACT':'SYNTHETIC · METHOD DEMONSTRATION';
    $('kind').classList.toggle('synthetic',meta.kind==='synthetic');$('origin').textContent=meta.kind==='observed'?'DE Africa':'Synthetic';
    $('view-title').textContent=meta.title;$('units').textContent=meta.units;
    $('legend-min').textContent=meta.range[0].toFixed(2);$('legend-max').textContent=meta.range[1].toFixed(2);$('gradient').style.background=gradient(meta.palette);
    $('provenance').textContent=`${meta.source}. License: ${meta.license}. ${meta.description}`;
    $('predicate').value=meta.id==='ngami'&&$('mode').value==='cube'?'value > 0.05':'value >= 0';
    rows=await engine.filter($('predicate').value);render(true);status('Ready · Zarr decoded / SQL connected');
    const url=new URL(location.href);url.searchParams.set('dataset',meta.id);history.replaceState(null,'',url);
    loaded=true;
  }catch(e){rows=[];render(true);status('Unable to load: '+e.message+'. Select another dataset or reload to retry.',true);}
  finally{lock(false);if(!loaded)for(const id of ['query','export','play'])$(id).disabled=true;}
}
$('query').onclick=query;$('predicate').onkeydown=e=>{if(e.ctrlKey&&e.key==='Enter')query();};
$('dataset').onchange=load;$('mode').onchange=()=>render(true);$('reset-view').onclick=resetView;$('time').oninput=()=>render();
$('clear-point').onclick=()=>{point=null;render();};
$('play').onclick=()=>{if(timer){stop();return;}$('play').textContent='Ⅱ Pause';timer=setInterval(()=>{$('time').value=(Number($('time').value)+1)%meta.times.length;render();},900);};
$('export').onclick=()=>{const blob=new Blob([JSON.stringify(geojson(rows,meta),null,2)],{type:'application/geo+json'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=meta.id+'-selection.geojson';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
window.addEventListener('pagehide',()=>{stop();engine?.dispose();deck?.finalize();});
async function main(){
  try{
    const response=await fetch(new URL('catalog.json',base));if(!response.ok)throw Error('Catalog HTTP '+response.status);catalog=await response.json();
    const boundaryResponse=await fetch(new URL('countries.geojson',base));boundaries=await boundaryResponse.json();
    for(const d of catalog){const option=document.createElement('option');option.value=d.id;option.textContent=d.title;$('dataset').append(option);}
    $('dataset').value=catalog.some(d=>d.id===params.get('dataset'))?params.get('dataset'):'ngami';
    if(['map','columns','cube','scene'].includes(params.get('mode')))$('mode').value=params.get('mode');
    deck=new Deck({parent:$('map'),controller:true,initialViewState:{longitude:22.7,latitude:-20.5,zoom:9},views:new MapView(),getCursor:({isDragging})=>isDragging?'grabbing':'crosshair',onError:e=>status('WebGL: '+e.message,true)});
    engine=await openEngine();await load();
  }catch(e){status('Startup failed: '+e.message+'. Try a current WebGL2-capable browser; the notebooks and data downloads remain available.',true);}
}
main();
