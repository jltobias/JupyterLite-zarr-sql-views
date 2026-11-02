"""Small SeasFire teaching extracts; NumPy/Matplotlib only until LexCube is used."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

DATA=Path('data')


def load_seasfire(region='ghana'):
    p=json.loads((DATA/'seasfire-provenance.json').read_text(encoding='utf-8'))
    r=next(r for r in p['regions'] if r['id']==region)
    with np.load(DATA/r['file'],allow_pickle=False) as archive:
        d={k:archive[k].copy() for k in archive.files}
    d['dates']=np.datetime64('2001-01-01')+d['days'].astype('timedelta64[D]')
    d['year']=d['dates'].astype('datetime64[Y]').astype(int)+1970
    d['duration_days']=np.diff(np.append(d['dates'],np.datetime64('2022-01-01'))).astype(int)
    d['bin']=np.concatenate([np.arange(np.sum(d['year']==y)) for y in np.unique(d['year'])])
    d['gwis_ba']=np.where(d['gwis_ba_valid_mask'][:,None,None]==1,d['gwis_ba'],np.nan)
    d['region']=r;d['provenance']=p
    d['metadata']=json.loads((DATA/'seasfire-zmetadata.json').read_text(encoding='utf-8'))['metadata']
    return d


def spatial_series(d, variable):
    """Burned area: strict sum. Intensive variables: available-area weighted mean."""
    a=d[variable].astype(float)
    if variable=='gwis_ba':
        return np.where(np.isfinite(a).all(axis=(1,2)),np.sum(a,axis=(1,2)),np.nan)
    w=np.where(np.isfinite(a),d['area'][None],0)
    denominator=w.sum(axis=(1,2))
    return np.divide(np.nansum(a*w,axis=(1,2)),denominator,
                     out=np.full(len(a),np.nan),where=denominator>0)


def seasonal_anomaly(series, bins, training):
    """Learn the seasonal baseline only on the selected training periods."""
    baseline=np.array([np.nanmean(series[training & (bins==b)]) for b in range(46)])
    return series-baseline[bins],baseline


def lag_correlation(driver, response, lag, selection):
    """Positive lag pairs driver[t-lag] with response[t], in source-bin steps."""
    if lag<0 or int(lag)!=lag or lag>=len(driver):
        raise ValueError('Lag must be an integer between zero and series length-1')
    x=driver if lag==0 else driver[:-lag]
    y=response if lag==0 else response[lag:]
    keep=selection.copy() if lag==0 else selection[lag:] & selection[:-lag]
    keep=keep & np.isfinite(x) & np.isfinite(y)
    n=int(keep.sum())
    if n<3 or np.std(x[keep])==0 or np.std(y[keep])==0:
        return np.nan,n
    return float(np.corrcoef(x[keep],y[keep])[0,1]),n


def raster(ax,d,values,title,*,vmin=0,vmax=None,cmap='inferno'):
    im=ax.pcolormesh(d['lon'],d['lat'],values,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax)
    ax.set(title=title,xlabel='Longitude (degrees east)',ylabel='Latitude (degrees north)')
    ax.set_aspect(1/np.cos(np.deg2rad(np.mean(d['lat']))))
    for axis in [ax.xaxis,ax.yaxis]: axis.set_major_locator(MaxNLocator(3))
    ax.ticklabel_format(useOffset=False,style='plain')
    return im


def data_array(d,variable='gwis_ba',start='2018-01-01'):
    import xarray as xr
    keep=d['dates']>=np.datetime64(start)
    attrs=d['metadata'][variable+'/.zattrs'].copy()
    attrs.update(source=d['provenance']['doi'],license='CC-BY-4.0')
    return xr.DataArray(d[variable][keep].copy(),dims=['time','latitude','longitude'],
        coords={'time':d['dates'][keep].astype('datetime64[ns]'),'latitude':d['lat'],'longitude':d['lon']},
        name=variable,attrs=attrs)
