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
  expect(selected).toBeGreaterThan(0);expect(selected).toBeLessThan(all);
  for(const mode of ['columns','cube','scene','map']){
    await page.locator('#mode').selectOption(mode);await expect(page.locator('#map canvas')).toBeVisible();
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
  await page.goto('/book/intro.html');await expect(page.getByRole('heading',{name:'Earth in the Browser',exact:true})).toBeVisible();
  await page.goto('/lite/lab/index.html?path=01_start_here.ipynb');
  await expect(page.getByRole('menuitem',{name:'File',exact:true})).toBeVisible({timeout:60000});
});
test('JupyterLite executes the Zarr and portable SQL lesson in Pyodide',async({page})=>{
  test.setTimeout(180000);
  await page.goto('/lite/lab/index.html?path=02_zarr_sql.ipynb',{waitUntil:'domcontentloaded'});
  await page.locator('.jp-Notebook').waitFor({timeout:60000});
  await expect(page.locator('body')).toContainText('Python (Pyodide) | Idle',{timeout:90000});
  await page.getByRole('menuitem',{name:'Run',exact:true}).click();
  await page.getByRole('menuitem',{name:'Run All Cells',exact:true}).click();
  await expect(page.locator('body')).toContainText('Python (Pyodide) | Busy',{timeout:30000});
  await expect(page.locator('body')).toContainText('Python (Pyodide) | Idle',{timeout:120000});
  await expect(page.locator('.jp-OutputArea-error')).toHaveCount(0);
  // Return to the top so the notebook's virtualized early outputs are inspected.
  await page.locator('.jp-Notebook').evaluate(e=>{e.scrollTop=0;});
  await expect(page.locator('body')).toContainText('Ready: Python + NumPy + local teaching data');
  await expect(page.locator('body')).not.toContainText('ModuleNotFoundError');
});
