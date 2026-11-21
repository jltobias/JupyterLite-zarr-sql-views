/* Earth in the Browser / eopf.js. Course contributors, 2026-11-21.
 * Input: pinned Sentinel-2 GeoZarr; output: two real browser maps.
 * OpenLayers 10.11 / EOxElements 2.10. Original teaching adapter, ISC.
 * Inspired by EOPF's OL and EOxElements tutorials; upstream notices retained.
 */
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import WebGLTile from 'ol/layer/WebGLTile.js';
import GeoZarr from 'ol/source/GeoZarr.js';
import {transformExtent} from 'ol/proj.js';
import 'ol/ol.css';
import '@eox/map';
import '@eox/map/src/plugins/advancedLayersAndSources';
import '@eox/layercontrol';
import '@eox/jsonform';

const $=id=>document.getElementById(id);
const provenance=await (await fetch('../data/eopf/provenance.json')).json();
const local=new URL('../data/eopf/classroom.zarr/',location.href).href;
const extent=transformExtent(provenance.bounds,'EPSG:32633','EPSG:3857');
const ol=new Map({target:'ol-map',view:new View({center:[0,0],zoom:10})});
const eox=$('eox-map');
await customElements.whenDefined('eox-map');
let generation=0;

function style(mode){
  if(mode==='ndvi'){
    const nir=['band',1],red=['band',2],sum=['+',nir,red];
    // A decimal literal avoids exponent formatting in OL's GLSL compiler.
    const index=['/', ['-',nir,red], ['case',['>',sum,0.000001],sum,0.000001]];
    return {color:['case',['all',['>=',nir,0],['>=',red,0],['>',sum,0.000001]],
      ['interpolate',['linear'],index,-1,'#663399',0,'#f5f0c5',0.5,'#56a469',1,'#005b46'],[0,0,0,0]]};
  }
  return {gamma:1.5,color:['color',...[1,2,3].map(i=>['interpolate',['linear'],['band',i],0,0,0.4,255]),1]};
}

function reset(){
  ol.getView().fit(extent,{padding:[25,25,25,25]});
  eox.zoomExtent=extent;
}

function update(){
  const current=++generation,mode=$('bands').value;
  const bands=mode==='ndvi'?['b08','b04']:mode==='false'?['b08','b04','b03']:['b04','b03','b02'];
  const url=$('source').value==='remote'?provenance.group_url:local;
  const styling=style(mode),source=new GeoZarr({url,bands,transition:0});
  $('status').textContent='Loading GeoZarr metadata and visible chunks…';
  source.on('tileloadend',()=>{if(current===generation)$('status').textContent='Ready · OpenLayers decoded GeoZarr pixels; compare the EOxElements map.';});
  source.on('tileloaderror',()=>{if(current===generation)$('status').textContent='A source chunk failed. Return to the bundled window or inspect the external service.';});
  source.on('change',()=>{if(source.getState()==='error'&&current===generation)$('status').textContent='Source metadata failed; select the bundled classroom window.';});
  ol.getLayers().clear();ol.addLayer(new WebGLTile({source,style:styling}));
  eox.layers=[{type:'WebGLTile',properties:{id:'sentinel',title:mode==='ndvi'?'NDVI (unmasked)':'Sentinel-2 reflectance'},source:{type:'GeoZarr',url,bands},style:styling}];
  $('configuration').textContent=JSON.stringify(eox.layers,null,2);
  $('legend').textContent=mode==='ndvi'?'NDVI: −1 purple → 0 cream → +1 dark green. No SCL cloud mask.':'Display stretch: reflectance 0–0.4; gamma 1.5. False color puts NIR in the red display channel.';
  reset();
}
$('bands').addEventListener('change',update);$('source').addEventListener('change',update);$('reset').addEventListener('click',reset);
update();
