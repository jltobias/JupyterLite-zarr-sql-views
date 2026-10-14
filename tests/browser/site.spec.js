import {test,expect} from '@playwright/test';
test('landing navigation is usable at desktop and mobile widths',async({page})=>{
  await page.goto('/');await expect(page.getByRole('heading',{name:/A changing Earth/})).toBeVisible();
  await expect(page.getByRole('link',{name:/Enter the Earth lab/})).toHaveAttribute('href','lab/');
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
test('Zarr decodes, DuckDB filters, four views render, export preserves origin',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/lab/?dataset=ngami');
  await expect(page.locator('#status')).toContainText('Ready',{timeout:60000});
  const all=Number((await page.locator('#count').textContent()).replaceAll(',',''));
  expect(all).toBeGreaterThan(0);
  await page.locator('#predicate').fill('value > 0.5 AND t = 0');await page.locator('#query').click();
  await expect(page.locator('#status')).toContainText('query applied');
  const selected=Number((await page.locator('#count').textContent()).replaceAll(',',''));
  expect(selected).toBe(127);expect(selected).toBeLessThan(all);
  const observedDownload=page.waitForEvent('download');await page.locator('#export').click();
  const observedFile=await (await observedDownload).path();
  const observed=JSON.parse(await (await import('node:fs/promises')).readFile(observedFile,'utf8'));
  expect(observed.features[0].geometry.coordinates[0]).toBeCloseTo(22.83625,8);
  expect(observed.features[0].geometry.coordinates[1]).toBeCloseTo(-20.425520833333334,8);
  expect(observed.features[0].properties.value).toBeCloseTo(.7045454383,7);
  expect(observed.provenance_url).toContain('deafrica-provenance.json');
  await page.locator('#predicate').fill('value > 0.5');await page.locator('#query').click();
  await expect(page.locator('#status')).toContainText('query applied');
  for(const mode of ['columns','cube','scene','map']){
    await page.locator('#mode').selectOption(mode);await expect(page.locator('#map canvas')).toBeVisible();
    await expect(page.locator('#map-note')).toContainText(mode==='cube'?'time index':mode==='scene'?'scaled value':'Drag to pan');
    if(mode==='cube')expect(await page.locator('#visible').textContent()).toBe(await page.locator('#count').textContent());
    else await expect(page.locator('#visible')).toHaveText('127');
  }
  await page.locator('#predicate').fill('value > 1000');await page.locator('#query').click();
  await expect(page.locator('#count')).toHaveText('0');await expect(page.locator('#chart')).toContainText('No matching cells');
  await page.locator('#predicate').fill('1=1; DROP TABLE cells');await page.locator('#query').click();
  await expect(page.locator('#status')).toContainText('Query rejected');
  await page.locator('#dataset').selectOption('heat');await expect(page.locator('#status')).toContainText('Ready');
  await expect(page.locator('#kind')).toContainText('SYNTHETIC');
  const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();const download=await downloadPromise;
  expect(download.suggestedFilename()).toBe('heat-selection.geojson');
  const path=await download.path();const fs=await import('node:fs/promises');const data=JSON.parse(await fs.readFile(path,'utf8'));
  expect(data.features[0].properties.kind).toBe('synthetic');expect(data.features.length).toBe(12*37*35);
  expect(errors).toEqual([]);
});
test('book and notebook runtime are assembled',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/book/intro.html');await expect(page.getByRole('heading',{name:'Earth in the Browser',exact:true})).toBeVisible();
  await page.goto('/book/notebooks/05_c3s_atlas.html');
  await expect(page.getByRole('heading',{name:/05 · C3S Atlas/})).toBeVisible();
  expect(errors).toEqual([]);
  await page.goto('/lite/lab/index.html?path=01_start_here.ipynb');
  await expect(page.getByRole('menuitem',{name:'File',exact:true})).toBeVisible({timeout:60000});
});
test('a failed load cannot relabel prior values through the keyboard shortcut',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/lab/?dataset=ngami');
  await page.locator('#reset-view').click();
  await expect(page.locator('#status')).toContainText('Ready',{timeout:60000});
  await page.route('**/heat.zarr/value/.zarray',route=>route.abort());
  await page.locator('#dataset').selectOption('heat');
  await expect(page.locator('#status')).toContainText('Unable to load');
  await page.locator('#predicate').fill('1=1');await page.locator('#predicate').press('Control+Enter');
  await expect(page.locator('#count')).toHaveText('0');
  await expect(page.locator('#query')).toBeDisabled();await expect(page.locator('#export')).toBeDisabled();
  expect(errors).toEqual([]);
});

test('oversized source metadata is rejected before chunk reads',async({page})=>{
  const chunks=[];page.on('request',r=>{if(/heat.zarr\/value\/\d/.test(r.url()))chunks.push(r.url());});
  await page.route('**/heat.zarr/value/.zarray',async route=>{
    const response=await route.fetch();const spec=await response.json();spec.shape=[365,2000,2000];
    await route.fulfill({response,json:spec});
  });
  await page.goto('/lab/?dataset=heat');
  await expect(page.locator('#status')).toContainText('Zarr dimensions do not match',{timeout:60000});
  expect(chunks).toEqual([]);
});

test('AR6 projected medians retain coordinates, scenario and baseline in all views',async({page})=>{
  await page.goto('/lab/?dataset=ar6_lagos&mode=columns');
  await expect(page.locator('#status')).toContainText('Ready',{timeout:60000});
  await expect(page.locator('#kind')).toContainText('PROJECTIONS');
  await expect(page.locator('#count')).toHaveText('225');
  await expect(page.locator('#visible')).toHaveText('25');
  await page.locator('#mode').selectOption('cube');await expect(page.locator('#visible')).toHaveText('225');
  await expect(page.locator('#map-note')).toContainText('time index');
  await page.locator('#predicate').fill('t=8 AND lat=6 AND lon=3');await page.locator('#query').click();
  await expect(page.locator('#count')).toHaveText('1');
  const download=page.waitForEvent('download');await page.locator('#export').click();
  const obj=JSON.parse(await (await import('node:fs/promises')).readFile(await (await download).path(),'utf8'));
  expect(obj.features[0].properties.time).toBe('2100');expect(obj.features[0].properties.kind).toBe('projected');
  expect(obj.features[0].geometry.coordinates).toEqual([3,6]);
  expect(obj.workflow).toBe('wf_1e');expect(obj.scenario).toBe('ssp585');expect(obj.baseline).toBe('1995–2014');
  expect(obj.provenance_url).toContain('ar6-provenance.json');
});

test('TESSERA similarity maps preserve their reference, native data identity and sampling',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/lab/?dataset=tessera_lagos&mode=cube');
  await expect(page.locator('#status')).toContainText('Ready',{timeout:60000});
  await expect(page.locator('#kind')).toHaveText('EMBEDDINGS · DERIVED SIMILARITY');
  await expect(page.locator('#count')).toHaveText('12,247');
  await expect(page.locator('#visible')).toHaveText('12,247');
  await page.locator('#predicate').fill('t = 2 AND row = 32 AND col = 32');
  await page.locator('#query').click();
  await expect(page.locator('#count')).toHaveText('1');
  for(const mode of ['columns','map','scene','cube']){
    await page.locator('#mode').selectOption(mode);
    await expect(page.locator('#map canvas')).toBeVisible();
  }
  const pending=page.waitForEvent('download');await page.locator('#export').click();
  const file=await (await pending).path();
  const data=JSON.parse(await (await import('node:fs/promises')).readFile(file,'utf8'));
  expect(data.features[0].properties.value).toBeCloseTo(1,7);
  expect(data.features[0].geometry.coordinates).toEqual([3.3631875,6.4388125]);
  expect(data.reference.year).toBe(2025);expect(data.dataset_variant).toBe('dclimate');
  expect(data.snapshot_id).toBe('B6AFRJGX5XQC0A716PA0');
  expect(data.license_url).toContain('zero/1.0');
  expect(data.sampling).toContain('10 m source pixels');
  await page.locator('#dataset').selectOption('tessera_abidjan');
  await expect(page.locator('#status')).toContainText('Ready');
  await expect(page.locator('#view-title')).toContainText('Abidjan');
  expect(errors).toEqual([]);
});

for(const slug of ['02_zarr_sql','13_ar6_archive','14_ar6_port_cities','15_ar6_grid_maps','16_ar6_uncertainty','17_tessera_embeddings','18_tessera_similarity','19_tessera_pca','20_tessera_clusters','21_tessera_change']){
  test(`JupyterLite fully executes ${slug} in Pyodide`,async({page})=>{
    test.setTimeout(240000);
    // Expose the application only inside this test to inspect every model output,
    // including virtualized cells. This does not alter the published configuration.
    await page.route('**/lite/lab/index.html*',async route=>{
      const response=await route.fetch();let html=await response.text();
      html=html.replace(/(<script id="jupyter-config-data"[^>]*>)([\s\S]*?)(<\/script>)/,
        (_,a,b,c)=>a+JSON.stringify({...JSON.parse(b),exposeAppInBrowser:true})+c);
      await route.fulfill({response,body:html});
    });
    await page.goto(`/lite/lab/index.html?path=${slug}.ipynb`,{waitUntil:'domcontentloaded'});
    await page.locator('.jp-Notebook').waitFor({timeout:60000});
    await expect(page.locator('body')).toContainText('Python (Pyodide) | Idle',{timeout:120000});
    await page.evaluate(async()=>{await window.jupyterapp.commands.execute('notebook:clear-all-cell-outputs');});
    const cleared=await page.evaluate(()=>window.jupyterapp.shell.currentWidget.content.model.toJSON());
    expect(cleared.cells.filter(c=>c.cell_type==='code').every(c=>c.outputs.length===0)).toBeTruthy();
    await page.evaluate(async()=>{await window.jupyterapp.commands.execute('notebook:run-all-cells');});
    const notebook=await page.evaluate(()=>window.jupyterapp.shell.currentWidget.content.model.toJSON());
    const cells=notebook.cells.filter(c=>c.cell_type==='code');
    expect(cells.flatMap(c=>c.outputs).filter(o=>o.output_type==='error')).toEqual([]);
    expect(cells.every(c=>c.execution_count!==null)).toBeTruthy();
    expect(JSON.stringify(cells.at(-1).outputs)).toContain(`LESSON COMPLETE: ${slug}`);
  });
}
