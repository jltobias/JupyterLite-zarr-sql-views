"""Small NumPy-only GeoTessera teaching operations; no native GIS dependencies.

Input embeddings retain the provider's int8 values and per-pixel float32 scales.
The native GeoTessera/Icechunk extraction is in scripts/prepare_tessera.py.
"""
from pathlib import Path
import json
import numpy as np


def load_tessera(city='lagos', data_dir=Path('data')):
    data_dir=Path(data_dir)
    p=json.loads((data_dir/'tessera-provenance.json').read_text(encoding='utf-8'))
    if city not in {c['id'] for c in p['cities']}:
        raise ValueError('Choose lagos or abidjan')
    files=[]
    for year in p['years']:
        with np.load(data_dir/f'tessera_{city}_{year}.npz', allow_pickle=False) as z:
            files.append({k:z[k] for k in z.files})
    for item in files[1:]:
        for name in ['lon','lat','native_lon','native_lat']:
            np.testing.assert_array_equal(item[name],files[0][name])
    q=np.stack([f['quantized'] for f in files])
    s=np.stack([f['scales'] for f in files])
    valid=np.isfinite(s)&(s>0)&(s<1e6)
    embedding=q.astype(np.float32)*np.where(valid,s,np.nan)[...,None]
    valid &= np.isfinite(embedding).all(axis=-1)&(np.linalg.norm(embedding,axis=-1)>0)
    embedding[~valid]=np.nan
    return dict(embedding=embedding,quantized=q,scales=s,valid=valid,
                years=np.array(p['years']),provenance=p,
                city=next(c for c in p['cities'] if c['id']==city),
                **{k:files[0][k] for k in ['lon','lat','native_lon','native_lat']},
                **{k:np.stack([f[k] for f in files]) for k in
                   ['s2_obs_count','s1_asc_obs_count','s1_desc_obs_count']})


def unit_vectors(x):
    """L2 normalize the last axis. Zero or missing vectors remain missing."""
    x=np.asarray(x,dtype=np.float64)
    norms=np.linalg.norm(x,axis=-1,keepdims=True)
    return np.divide(x,norms,out=np.full_like(x,np.nan),where=np.isfinite(norms)&(norms>0))


def fit_pca(x, n=3):
    """Fit centered PCA to finite rows. Keep one basis when comparing maps."""
    x=np.asarray(x,dtype=np.float64).reshape(-1,x.shape[-1])
    x=x[np.isfinite(x).all(axis=1)]
    if len(x)<2 or not 1<=n<=x.shape[1]:
        raise ValueError('PCA needs at least two valid rows and a valid component count')
    mean=x.mean(axis=0); centered=x-mean
    covariance=centered.T@centered/(len(x)-1)
    eigenvalues,basis=np.linalg.eigh(covariance)
    order=np.argsort(eigenvalues)[::-1]
    eigenvalues=np.maximum(eigenvalues[order],0)
    if eigenvalues.sum()<=0:
        raise ValueError('PCA needs nonzero variance')
    components=basis[:,order[:n]]
    # Fix arbitrary eigenvector signs for reproducible illustrations.
    signs=np.sign(components[np.argmax(np.abs(components),axis=0),np.arange(n)])
    components*=np.where(signs==0,1,signs)
    return dict(mean=mean,components=components,explained=eigenvalues[:n]/eigenvalues.sum(),
                count=len(x))


def project(x, model):
    return (x-model['mean'])@model['components']


def rgb_limits(scores):
    flat=scores.reshape(-1,3)
    valid=flat[np.isfinite(flat).all(axis=1)]
    return np.percentile(valid,[2,98],axis=0)


def rgb(scores, limits):
    lo,hi=limits
    color=np.clip((scores-lo)/np.maximum(hi-lo,1e-12),0,1)
    # Explicit gray for missing pixels. Color has no physical units.
    return np.where(np.isfinite(color).all(axis=-1,keepdims=True),color,.75)


def spherical_kmeans(x,k=4,seed=7,iterations=40):
    """Lloyd iterations on unit vectors; cluster numbers carry no semantics."""
    x=unit_vectors(np.asarray(x).reshape(-1,x.shape[-1]))
    x=x[np.isfinite(x).all(axis=1)]
    if len(x)<k or k<2:
        raise ValueError('Need at least k valid samples and k >= 2')
    rng=np.random.default_rng(seed)
    centers=x[rng.choice(len(x),k,replace=False)].copy()
    for _ in range(iterations):
        labels=np.argmax(x@centers.T,axis=1)
        new=[]
        for i in range(k):
            group=x[labels==i]
            v=group.mean(axis=0) if len(group) else x[rng.integers(len(x))]
            new.append(v/np.linalg.norm(v) if np.linalg.norm(v)>0 else centers[i])
        new=np.asarray(new)
        if np.max(np.abs(new-centers))<1e-7:
            centers=new
            break
        centers=new
    return centers


def assign_clusters(x,centers):
    u=unit_vectors(x); valid=np.isfinite(u).all(axis=-1)
    scores=np.where(valid[...,None],u,0)@centers.T
    labels=np.where(valid,np.argmax(scores,axis=-1),-1)
    distance=np.where(valid,1-np.max(scores,axis=-1),np.nan)
    return labels,distance


def adjusted_rand(a,b):
    """Permutation-invariant agreement between two partitions; missing excluded."""
    a,b=np.asarray(a).ravel(),np.asarray(b).ravel()
    valid=(a>=0)&(b>=0); a,b=a[valid],b[valid]
    if len(a)<2:
        return np.nan
    _,a=np.unique(a,return_inverse=True); _,b=np.unique(b,return_inverse=True)
    table=np.zeros((a.max()+1,b.max()+1),dtype=np.int64)
    np.add.at(table,(a,b),1)
    pairs=lambda counts: np.sum(counts*(counts-1)/2)
    observed=pairs(table); left=pairs(table.sum(axis=0)); right=pairs(table.sum(axis=1))
    expected=left*right/(len(a)*(len(a)-1)/2)
    maximum=(left+right)/2
    return 1.0 if maximum==expected else float((observed-expected)/(maximum-expected))


def scalar_map(ax,d,values,title,**kwargs):
    im=ax.pcolormesh(d['lon'],d['lat'],values,shading='nearest',**kwargs)
    ax.set(xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)',title=title)
    ax.set_aspect(1/np.cos(np.deg2rad(d['city']['center'][1])))
    ax.ticklabel_format(useOffset=False)
    return im


def export_points(d,values,path,threshold=.9,reference=(2,32,32)):
    """Export values at actual native pixel centers, with complete provenance."""
    t0,r0,c0=reference
    u=unit_vectors(d['embedding']); ref=u[t0,r0,c0]
    if not np.isfinite(ref).all():
        raise ValueError('Reference must be a valid vector')
    expected=np.clip(np.sum(u*ref,axis=-1),-1,1)
    if np.shape(values)!=expected.shape or not np.allclose(values,expected,atol=1e-6,equal_nan=True):
        raise ValueError('Values do not match the stated cosine reference')
    good=np.isfinite(values)&(values>=threshold)
    result=dict(type='FeatureCollection',name=d['city']['title'],license='CC0-1.0',
                license_url=d['provenance']['license_url'],
                source=d['provenance']['store'],snapshot_id=d['provenance']['snapshot_id'],
                dataset_version='1.1',dataset_variant='dclimate',
                provenance_url='https://jltobias.github.io/JupyterLite-zarr-sql-views/data/tessera-provenance.json',
                method=f'Cosine similarity to {d["years"][t0]} native pixel at query grid row={r0}, col={c0}; full 128 dimensions; normalized vectors.',
                reference_native_lon=float(d['native_lon'][r0,c0]),reference_native_lat=float(d['native_lat'][r0,c0]),
                warning='Exploratory embedding similarity, not verified classes or hazards.',features=[])
    for t,r,c in np.argwhere(good):
        result['features'].append(dict(type='Feature',geometry=dict(type='Point',coordinates=
            [float(d['native_lon'][r,c]),float(d['native_lat'][r,c])]),properties=dict(
                year=int(d['years'][t]),row=int(r),col=int(c),cosine_similarity=float(values[t,r,c]),
                query_lon=float(d['lon'][c]),query_lat=float(d['lat'][r]))))
    Path(path).write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    return result
