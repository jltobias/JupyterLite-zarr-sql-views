import {defineConfig} from 'vite';
import {resolve} from 'node:path';
export default defineConfig({
  base: './',
  build: {rollupOptions: {input: {home: resolve('index.html'), lab: resolve('lab/index.html')}}},
});
