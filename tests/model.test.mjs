import test from 'node:test';
import assert from 'node:assert/strict';
import {flattenCube,validatePredicate,timeSummary,geojson} from '../src/model.js';

test('flattening preserves time, descending latitude, and nulls',()=>{
  const meta={shape:[2,2,2],lon:[10,11],lat:[3,2]};
  const rows=flattenCube(new Float32Array([1,2,3,NaN,5,6,7,8]),meta);
  assert.deepEqual(rows[6],{id:6,t:1,row:1,col:0,lon:10,lat:2,value:7});
  assert.equal(rows[3].value,null);
});
test('numeric SQL grammar rejects statements, subqueries, comments and remote reads',()=>{
  assert.equal(validatePredicate('value > 0.5 AND lat BETWEEN -30 AND 5'),'value > 0.5 AND lat BETWEEN -30 AND 5');
  assert.equal(validatePredicate('value > 1e-3'),'value > 1e-3');
  for(const p of ['1=1; DROP TABLE cells',"value IN (SELECT value FROM cells)",'1--comment',"read_csv('https://example.com')",'1/* comment */'])assert.throws(()=>validatePredicate(p));
});
test('empty time windows stay gaps and GeoJSON carries data origin',()=>{
  const rows=[{t:0,value:2,lon:10,lat:-3},{t:0,value:4,lon:11,lat:-3}];
  assert.deepEqual(timeSummary(rows,['a','b']).map(r=>r.mean),[3,null]);
  const out=geojson(rows,{title:'Example',times:['a'],license:'CC0-1.0',source:'test',description:'synthetic',kind:'synthetic',units:'m'});
  assert.deepEqual(out.features[0].geometry.coordinates,[10,-3]);
  assert.equal(out.features[0].properties.kind,'synthetic');
});
