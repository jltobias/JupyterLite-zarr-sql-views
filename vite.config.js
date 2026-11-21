import {defineConfig} from 'vite';
import {resolve} from 'node:path';
export default defineConfig({
  base: './',
  define: {__VUE_OPTIONS_API__: true, __VUE_PROD_DEVTOOLS__: false, __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false},
  build: {rollupOptions: {input: {home: resolve('index.html'), lab: resolve('lab/index.html'), eopf: resolve('eopf/index.html'), dashboard: resolve('eopf-dashboard.html')}}},
});
