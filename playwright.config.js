import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/browser',timeout:90000,workers:1,
  use:{baseURL:process.env.TEST_BASE_URL||'http://127.0.0.1:8000',headless:true,
    launchOptions:{args:['--enable-unsafe-swiftshader']},screenshot:'only-on-failure'},
});
