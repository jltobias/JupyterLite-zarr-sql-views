// Small, inspectable transformations shared by the browser and unit checks.
export function flattenCube(data, meta) {
  const [nt,ny,nx]=meta.shape;
  if(data.length!==nt*ny*nx) throw Error('Zarr shape and decoded values disagree');
  return Array.from(data,(value,id)=>{
    const col=id%nx,row=Math.floor(id/nx)%ny,t=Math.floor(id/(nx*ny));
    return {id,t,row,col,lon:meta.lon[col],lat:meta.lat[row],value:Number.isFinite(value)?value:null};
  });
}
export function validatePredicate(text) {
  text=text.trim()||'1=1';
  if(text.length>500) throw Error('Use a predicate shorter than 500 characters.');
  const tokens=text.match(/(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?|[A-Za-z_]+|<=|>=|<>|!=|[()=<>+*/%-]/gi)||[];
  if(tokens.join('').toLowerCase()!==text.replace(/\s/g,'').toLowerCase()) throw Error('Only numeric SQL predicates are supported.');
  const allowed=new Set(['value','lon','lat','t','row','col','id','and','or','not','is','null','between','true','false']);
  for(const token of tokens) if(/^[a-z_]+$/i.test(token)&&!allowed.has(token.toLowerCase())) throw Error(`Unsupported name: ${token}`);
  if(/--|\/\*/.test(text)) throw Error('Comments are not allowed in a predicate.');
  return text;
}
export function timeSummary(rows, times) {
  return times.map((label,t)=>{
    const values=rows.filter(r=>r.t===t).map(r=>r.value).filter(Number.isFinite);
    return {label,t,n:values.length,mean:values.length?values.reduce((a,b)=>a+b,0)/values.length:null};
  });
}
export function geojson(rows,meta) {
  return {type:'FeatureCollection',name:meta.title,license:meta.license,source:meta.source,
    description:meta.description,features:rows.map(({lon,lat,...r})=>({type:'Feature',
      geometry:{type:'Point',coordinates:[lon,lat]},properties:{...r,time:meta.times[r.t],units:meta.units,kind:meta.kind}}))};
}
