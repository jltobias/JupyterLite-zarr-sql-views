"""Reproducible small Zarr v2 teaching stores; no credentials required.

Synthetic cubes are analytic demonstrations, never observations or forecasts.
Run --refresh-deafrica to obtain a 48 x 48 nearest-neighbour sample from real COGs.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import urllib.request
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'public/data'
MANIFEST = []

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')

def cube(key, title, values, lon, lat, times, units, kind, description, palette='thermal', extra=None):
    values = np.asarray(values, dtype='<f4')
    folder = DATA / f'{key}.zarr'
    write_json(folder / '.zgroup', {'zarr_format': 2})
    entry = dict(id=key, title=title, shape=list(values.shape), lon=list(map(float,lon)),
                 lat=list(map(float,lat)), times=times, units=units, kind=kind,
                 description=description, palette=palette, store=f'{key}.zarr',
                 range=[float(np.nanmin(values)),float(np.nanmax(values))])
    entry.update(extra or {})
    write_json(folder / '.zattrs', entry)
    shape = list(values.shape)
    write_json(folder / 'value/.zarray', dict(zarr_format=2, shape=shape, chunks=[1,*shape[1:]],
               dtype='<f4', compressor=None, fill_value='NaN', order='C', filters=None))
    write_json(folder / 'value/.zattrs', {'_ARRAY_DIMENSIONS':['time','latitude','longitude'], 'units':units})
    for t in range(shape[0]):
        (folder / f'value/{t}.0.0').write_bytes(values[t].tobytes())
    for name, arr in [('longitude',lon),('latitude',lat),('time',range(shape[0]))]:
        write_json(folder / name / '.zarray',dict(zarr_format=2,shape=[len(arr)],chunks=[len(arr)],
                    dtype='<f8',compressor=None,fill_value=None,order='C',filters=None))
        write_json(folder / name / '.zattrs',{'_ARRAY_DIMENSIONS':[name]})
        (folder/name/'0').write_bytes(np.asarray(arr,dtype='<f8').tobytes())
    zip_path = ROOT / 'notebooks/data' / f'{key}.zip'
    zip_path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(folder).as_posix(),date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(info,p.read_bytes())
    entry['sha256_notebook_zip'] = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    MANIFEST.append(entry)

def deafrica(refresh):
    cache = DATA / 'deafrica-extract.npz'
    provenance = DATA / 'deafrica-provenance.json'
    if refresh or not cache.exists():
        import rasterio
        from rasterio.warp import reproject, Resampling
        from rasterio.transform import from_bounds
        years=[2018,2020,2022]
        # Entire window lies inside x203/y050, EPSG:6933 source tile.
        bounds=[22.60,-20.60,22.88,-20.35]
        transform=from_bounds(*bounds,48,48)
        stack=[]; records=[]
        for year in years:
            search=f'https://explorer.digitalearth.africa/stac/search?collections=wofs_ls_summary_annual&bbox=22.70,-20.50,22.71,-20.49&datetime={year}-01-01/{year}-12-31&limit=1'
            with urllib.request.urlopen(search,timeout=90) as r:
                item=json.load(r)['features'][0]
            def url(band):
                return item['assets'][band]['href'].replace('s3://deafrica-services/','https://deafrica-services.s3.af-south-1.amazonaws.com/')
            bands={}
            for band in ['frequency','count_clear']:
                local=ROOT/'.work'/f'ngami-{year}-{band}.tif'
                if refresh or not local.exists():
                    print('Downloading',url(band),flush=True)
                    urllib.request.urlretrieve(url(band),local)
                with rasterio.open(local) as src:
                    dest=np.full((48,48),np.nan,dtype='float32')
                    reproject(rasterio.band(src,1),dest,src_transform=src.transform,src_crs=src.crs,
                              src_nodata=src.nodata,dst_transform=transform,dst_crs='EPSG:4326',
                              dst_nodata=np.nan,resampling=Resampling.nearest)
                    bands[band]=dest
            # Small observation counts cannot support a reliable annual frequency.
            values=np.where(bands['count_clear']>=5,bands['frequency'],np.nan)
            stack.append(values)
            records.append(dict(year=year,item_id=item['id'],search=search,
                           frequency_url=url('frequency'),count_clear_url=url('count_clear')))
        np.savez_compressed(cache,value=np.stack(stack),lon=np.linspace(bounds[0]+(bounds[2]-bounds[0])/96,bounds[2]-(bounds[2]-bounds[0])/96,48),
                            lat=np.linspace(bounds[3]-(bounds[3]-bounds[1])/96,bounds[1]+(bounds[3]-bounds[1])/96,48))
        write_json(provenance,dict(provider='Digital Earth Africa',product='wofs_ls_summary_annual',license='CC-BY-4.0',
            retrieved='2026-10-04',bounds=bounds,source_crs='EPSG:6933',output_crs='EPSG:4326',
            method='Nearest-neighbour point sampling on a 48 by 48 geographic grid; count_clear < 5 masked; not an area average.',
            records=records,source_docs='https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html'))
    d=np.load(cache)
    cube('ngami','Lake Ngami · observed surface water',d['value'],d['lon'],d['lat'],['2018','2020','2022'],
         'water detection frequency (0–1)','observed',
         'Digital Earth Africa WOfS annual summary, sampled and reprojected. Clear-observation count ≥ 5. Water presence is not water quality or water availability.',
         'ocean',{'source':'Digital Earth Africa / Landsat','license':'CC-BY-4.0','provenance':'deafrica-provenance.json'})

def synthetic():
    lon=np.linspace(-18,50,35); lat=np.linspace(37,-35,37)
    x,y=np.meshgrid(lon,lat); months=np.arange(12)[:,None,None]
    # Analytic equations deliberately avoid being mistaken for measured climate.
    heat=26+9*np.exp(-((y[None]-19)/15)**2)+5*np.sin(2*np.pi*(months-2)/12)*np.sin(np.deg2rad(y))[None]+1.4*np.cos(x[None]/9)
    air=12+34*np.exp(-((y[None]-18)/10)**2)*(1+.45*np.cos(2*np.pi*months/12))+5*np.cos(x[None]/11)**2
    rain=70+60*np.cos(2*np.pi*(months/12-y[None]/90))+25*np.cos(x[None]/14)
    times=[f'2000-{m:02d}' for m in range(1,13)]
    for key,title,v,unit,desc,pal in [
        ('heat','Africa · heat laboratory',heat,'air temperature (°C)','Analytic seasonal temperature field. Not ERA5, UTCI, wet-bulb temperature, or an observed heat event.','thermal'),
        ('air','Africa · air-quality laboratory',air,'illustrative PM2.5 (µg/m³)','Invented aerosol field for exposure reasoning. Not CAMS data, measured pollution, or a health assessment.','ember'),
        ('rain','Africa · food & water laboratory',rain,'illustrative rainfall (mm/month)','Invented rainfall field for seasonality and threshold sensitivity. Not CHIRPS, crop yield, or a food-insecurity forecast.','ocean')]:
        cube(key,title,v,lon,lat,times,unit,'synthetic',desc,pal,{'source':'Analytic equations in scripts/prepare_data.py','license':'CC0-1.0'})
    lon=np.linspace(31.00,31.12,32); lat=np.linspace(-29.84,-29.96,32)
    x,y=np.meshgrid(np.linspace(0,1,32),np.linspace(0,1,32))
    elev=5*x+1.4*np.sin(8*y)*x+0.7*np.sin(15*x)*np.sin(12*y)
    cube('coast','Coastal futures · illustrative terrain',elev[None],lon,lat,['hypothetical'],
         'illustrative elevation (m)','synthetic','Invented terrain near Durban coordinates. No real DEM, vertical datum, drainage, tides, defenses, or flood hydraulics. Height threshold is not inundation risk.',
         'ocean',{'source':'Analytic equation in scripts/prepare_data.py','license':'CC0-1.0'})
    lon=np.linspace(33.0,33.5,30); lat=np.linspace(-0.1,-0.6,30)
    x,y=np.meshgrid(np.linspace(0,1,30),np.linspace(0,1,30))
    red=.03+.04*np.exp(-((x[None]-.1-months/20)**2+(y[None]-.5)**2)/.025)
    cube('water','Water quality · optical proxy laboratory',red,lon,lat,times,
         'illustrative red reflectance (0–1)','synthetic','Invented reflectance plume at Lake Victoria coordinates. Reflectance is not pathogen concentration, turbidity calibration, chlorophyll, or drinking-water safety.',
         'ocean',{'source':'Analytic equation in scripts/prepare_data.py','license':'CC0-1.0'})

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--refresh-deafrica',action='store_true'); a=p.parse_args()
    DATA.mkdir(parents=True,exist_ok=True)
    deafrica(a.refresh_deafrica); synthetic()
    write_json(DATA/'catalog.json',MANIFEST)
    write_json(ROOT/'notebooks/data/catalog.json',MANIFEST)
    print('Prepared',len(MANIFEST),'Zarr stores')
