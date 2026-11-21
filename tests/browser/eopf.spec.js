import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';

test('EOPF maps decode GeoZarr, switch bands and render NDVI',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/eopf/');
  await expect(page.locator('#status')).toContainText('Ready',{timeout:60000});
  const map=page.locator('eox-map');
  const centerData=()=>map.evaluate(el=>{
    const m=el.map,pixel=m.getPixelFromCoordinate(m.getView().getCenter());
    const data=m.getLayers().item(0)?.getData(pixel);
    return data?Array.from(data):null;
  });
  await expect.poll(centerData,{timeout:30000}).not.toBeNull();
  const rgb=await centerData();expect(rgb[0]).toBeGreaterThan(0);expect(rgb[0]).toBeLessThan(1);
  await page.locator('#bands').selectOption('false');
  await expect.poll(async()=>{const data=await centerData();return !!data && data[0]!==rgb[0];},{timeout:30000}).toBe(true);
  const falseColor=await centerData();expect(falseColor[1]).toBeCloseTo(rgb[0],4);
  await page.locator('#bands').selectOption('ndvi');
  await expect(page.locator('#legend')).toContainText('No SCL cloud mask');
  await expect.poll(()=>map.evaluate(el=>el.layers[0].source.bands)).toEqual(['b08','b04']);
  await expect.poll(centerData,{timeout:30000}).not.toBeNull();
  await page.screenshot({path:test.info().outputPath('eopf-ndvi.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  expect(errors).toEqual([]);
});

test('eodash stays on demand and exposes its reproducible configuration',async({page})=>{
  // Pin the catalog response so CI tests the real component without relying on
  // today's external inventory. Live item selection is a separate manual check.
  const collection=JSON.parse(await readFile('public/data/eopf/collection.json','utf8'));
  const item=JSON.parse(await readFile('public/data/eopf/item.json','utf8'));
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://api.explorer.eopf.copernicus.eu/stac**',async route=>{
    const path=new URL(route.request().url()).pathname;
    let body;
    if(path.endsWith('/search')||path.endsWith('/items'))body={type:'FeatureCollection',features:[item],links:[],numberMatched:1,numberReturned:1};
    else if(path.endsWith('/collections'))body={collections:[collection],links:[]};
    else if(path.endsWith('/queryables'))body={type:'object',properties:{}};
    else if(path.includes('/collections/'))body=collection;
    else body={type:'Catalog',id:'test-eopf',stac_version:'1.1.0',description:'Recorded teaching fixture',links:[],conformsTo:[]};
    await route.fulfill({json:body});
  });
  const requests=[];page.on('request',r=>{if(r.url().includes('api.explorer.eopf'))requests.push(r.url());});
  await page.goto('/eopf-dashboard.html');
  await expect(page.getByRole('button',{name:'Load live eodash explorer'})).toBeVisible();
  await expect(page.locator('#status')).toContainText('Not loaded');
  expect(requests).toEqual([]);
  const config=await (await page.request.get('/data/eopf/eodash-config.json')).json();
  expect(config.stacEndpoint).toEqual({endpoint:'https://api.explorer.eopf.copernicus.eu/stac',api:true});
  await page.getByRole('button',{name:'Load live eodash explorer'}).click();
  await expect(page.locator('eox-itemfilter').getByText(item.id,{exact:true})).toBeVisible({timeout:60000});
  await expect(page.locator('eox-map#main canvas').first()).toBeVisible();
  expect(requests.some(url=>url.includes('/search'))).toBeTruthy();
  expect(errors).toEqual([]);
});
