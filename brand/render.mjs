// Renders the Clean by Morning social images from HTML, using the site's own font and photos.
// Usage: node brand/render.mjs   (needs Playwright with a Chromium browser)
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { writeFileSync, unlinkSync } from 'node:fs';

const here = dirname(fileURLToPath(import.meta.url));
const site = join(here, '..', 'site', 'static');
const font = w => `url("file://${site}/fonts/sentient-${w}.woff2")`;
const img = f => `file://${site}/img/${f}`;
const base = `
@font-face { font-family: S; src: ${font(300)}; font-weight: 300; }
@font-face { font-family: S; src: ${font(400)}; font-weight: 400; }
@font-face { font-family: S; src: ${font(500)}; font-weight: 500; }
* { box-sizing: border-box; margin: 0; }
body { width: var(--w); height: var(--h); overflow: hidden; background: #0034eb; color: #fff; font-family: S, Georgia, serif; position: relative; }
.photo { position: absolute; inset: 0; background: #0034eb; }
.photo img { width: 100%; height: 100%; object-fit: cover; mix-blend-mode: luminosity; opacity: .55; }
.band { position: absolute; background: rgb(0 18 90 / .62); }
.bar { background: #e9e34a; }
`;
const assets = [
  { file: 'profile-1080.png', w: 1080, h: 1080, html: `
    <div style="position:absolute;inset:0;display:grid;place-items:center;text-align:center">
      <div><div style="font-weight:300;font-size:150px;line-height:.95;letter-spacing:-.02em">Clean<br>by Morning</div>
      <div class="bar" style="width:360px;height:34px;margin:56px auto 0"></div></div></div>` },
  { file: 'linkedin-banner-1584x396.png', w: 1584, h: 396, html: `
    <div class="photo"><img src="${img('brooklyn-bridge-lower-manhattan-night.webp')}" style="object-position:center 60%"></div>
    <div style="position:absolute;right:80px;top:70px;text-align:right">
      <div style="font-weight:300;font-size:92px;line-height:.95">Medical offices,<br>clean by morning</div>
      <div style="font-size:30px;margin-top:22px"><span class="band" style="position:static;padding:4px 12px">Brooklyn · Manhattan · Nassau County</span></div></div>` },
  { file: 'facebook-cover-1640x624.png', w: 1640, h: 624, html: `
    <div class="photo"><img src="${img('brooklyn-bridge-lower-manhattan-night.webp')}" style="object-position:center 62%"></div>
    <div style="position:absolute;left:0;right:0;top:120px;text-align:center">
      <div style="font-weight:300;font-size:120px;line-height:.92">Medical offices,<br>clean by morning</div>
      <div style="font-size:34px;margin-top:34px"><span class="band" style="position:static;padding:6px 14px">Evening cleaning in Brooklyn, Manhattan and Nassau County</span></div></div>` },
  { file: 'google-business-cover-1080x608.png', w: 1080, h: 608, html: `
    <div class="photo"><img src="${img('lit-office-windows-at-night.webp')}"></div>
    <div style="position:absolute;left:64px;bottom:64px">
      <div style="font-weight:300;font-size:96px;line-height:.92">You lock up.<br>We clean.</div>
      <div class="bar" style="width:220px;height:22px;margin-top:30px"></div></div>` },
  { file: 'instagram-post-1080x1350.png', w: 1080, h: 1350, html: `
    <div class="photo" style="bottom:45%"><img src="${img('rain-on-window-city-lights.webp')}"></div>
    <div style="position:absolute;left:72px;right:72px;bottom:90px">
      <div style="font-weight:300;font-size:118px;line-height:.95">You leave at 6.<br>It's clean<br>by 7.</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:56px;font-size:34px">
        <span>Clean by Morning</span><span class="bar" style="color:#111;padding:10px 20px">Book a walkthrough</span></div></div>` },
  { file: 'wordmark-on-blue.png', w: 1600, h: 500, html: `
    <div style="position:absolute;inset:0;display:grid;place-items:center"><div style="font-weight:400;font-size:170px;letter-spacing:-.02em">Clean by Morning</div></div>` },
  { file: 'wordmark-on-white.png', w: 1600, h: 500, bg: '#ffffff', html: `
    <div style="position:absolute;inset:0;display:grid;place-items:center;color:#0034eb"><div style="font-weight:400;font-size:170px;letter-spacing:-.02em">Clean by Morning</div></div>` },
];

const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
for (const a of assets) {
  const page = await browser.newPage({ viewport: { width: a.w, height: a.h } });
  const tmp = join(here, '.render-tmp.html');
  writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><style>:root{--w:${a.w}px;--h:${a.h}px}${base}${a.bg ? `body{background:${a.bg}}` : ''}</style></head><body>${a.html}</body></html>`);
  await page.goto('file://' + tmp, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  unlinkSync(tmp);
  await page.waitForTimeout(400);
  await page.screenshot({ path: join(here, a.file) });
  console.log('rendered', a.file);
  await page.close();
}
await browser.close();
