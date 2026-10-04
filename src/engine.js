// Teaching adaptation of dzole0311/zarr-sql-views (ISC), src/analysis/runtime.ts.
// See licenses/zarr-sql-views-ISC.txt and THIRD_PARTY_NOTICES.md.
import {AsyncDuckDB, VoidLogger} from '@duckdb/duckdb-wasm';
import wasmURL from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url';
import workerURL from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url';
import {tableFromArrays, tableToIPC} from 'apache-arrow';
import * as zarr from 'zarrita';
import {validatePredicate, flattenCube} from './model.js';

export async function openEngine() {
  const worker = new Worker(workerURL);
  const db = new AsyncDuckDB(new VoidLogger(), worker);
  await db.instantiate(wasmURL);
  const connection = await db.connect();
  await connection.query("SET memory_limit='128MB'; SET threads=1; SET enable_external_access=false;");
  return {
    async load(meta, base) {
      if (meta.shape.reduce((a,b)=>a*b,1)>100000) throw Error('Teaching limit: 100,000 cells. Choose a smaller window.');
      const root = zarr.root(new zarr.FetchStore(new URL(meta.store+'/',base)));
      const array = await zarr.open(root.resolve('value'), {kind:'array'});
      const result = await zarr.get(array);
      const rows = flattenCube(result.data, meta);
      await connection.query('DROP TABLE IF EXISTS cells');
      const columns = Object.fromEntries(Object.keys(rows[0]).map(k=>[k, rows.map(r=>r[k])]));
      await connection.insertArrowFromIPCStream(tableToIPC(tableFromArrays(columns)),{name:'cells',create:true});
      return rows.length;
    },
    async filter(predicate) {
      const safe = validatePredicate(predicate);
      const result = await connection.query(`SELECT * FROM cells WHERE value IS NOT NULL AND (${safe}) ORDER BY t, row, col`);
      return result.toArray().map(r=>r.toJSON());
    },
    dispose(){ worker.terminate(); },
  };
}
