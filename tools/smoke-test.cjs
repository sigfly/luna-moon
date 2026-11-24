const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, hasTouch: true, isMobile: true });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/*', route => /^https?:/.test(route.request().url()) ? route.abort() : route.continue());
    await page.goto(pathToFileURL(path.join(__dirname, '../index.html')).href, { timeout: 120000 });
    await page.waitForFunction(() => document.getElementById('notice').hidden || document.getElementById('notice').textContent.includes('Unable'), { timeout: 120000 });
    assert(await page.locator('#notice').evaluate(el => el.hidden), await page.locator('#notice').textContent());
    assert.match(await page.locator('#resolution').textContent(), /4,096/);
    await page.waitForTimeout(700);
    const pixel = await page.locator('#globe').evaluate(canvas => { const g = canvas.getContext('webgl2'), p = new Uint8Array(4); g.readPixels(canvas.width / 2, canvas.height / 2, 1, 1, g.RGBA, g.UNSIGNED_BYTE, p); return [...p]; });
    assert.equal(pixel[3], 255, `Globe center must be opaque: ${pixel}`);
    await page.screenshot({ path: path.join(__dirname, '../.cache/moon-test.png') });
    await page.locator('#terrain').click();
    assert.match(await page.locator('#mapTag').textContent(), /elevation/i);
    await page.locator('#far').click();
    await page.waitForFunction(() => document.getElementById('hemisphere').textContent.includes('Far side'));
    await page.locator('#location').selectOption('0');
    assert.match(await page.locator('#info').textContent(), /Apollo 11/);
    await page.locator('#plus').click();
    await page.locator('#grid').check();
    assert.deepEqual(errors, []);
    console.log('Offline render, center pixel, elevation, far-side preset, landmark, zoom and grid passed.', pixel);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
