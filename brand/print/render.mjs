// Renders the Clean by Morning print kit as letter-size PDFs, using the site's own font.
// Usage: node brand/print/render.mjs   (needs Playwright with a Chromium browser)
// Print at 100% scale ("Actual size"), not "Fit to page", so cards and labels line up.
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { writeFileSync, unlinkSync } from 'node:fs';

const here = dirname(fileURLToPath(import.meta.url));
const fonts = join(here, '..', '..', 'site', 'static', 'fonts');
const font = w => `url("file://${fonts}/sentient-${w}.woff2")`;

const B = {
  name: 'Clean by Morning',
  owner: 'Jamel Potts',
  phone: '(516) 518-1731',
  email: 'jamel@cleanbymorning.com',
  web: 'cleanbymorning.com',
  line: 'Evening commercial cleaning',
  areas: 'Brooklyn · Manhattan · Nassau County',
};
const COBALT = '#0034eb', INK = '#0a1f7a', SUN = '#e9e34a';
const mark = s => `<svg width="${s}" height="${s}" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" fill="${COBALT}"/><rect x="14" y="40" width="36" height="10" fill="${SUN}"/></svg>`;

const base = (size) => `
@page { size: ${size}; margin: 0; }
@font-face { font-family: S; src: ${font(300)}; font-weight: 300; }
@font-face { font-family: S; src: ${font(400)}; font-weight: 400; }
@font-face { font-family: S; src: ${font(500)}; font-weight: 500; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; color: ${INK}; font-family: S, Georgia, serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.num { font-variant-numeric: tabular-nums; }
.bar { background: ${SUN}; }
`;

// 1. Car-window or desk sign (landscape)
const sign = `<style>${base('letter landscape')}
.page { width: 11in; height: 8.5in; padding: .6in .8in; display: flex; flex-direction: column; justify-content: center; }
.top { display: flex; align-items: center; gap: .35in; }
.name { font-size: 92pt; font-weight: 300; letter-spacing: -.02em; line-height: 1; color: ${COBALT}; }
.what { font-size: 30pt; margin-top: .35in; }
.phone { font-size: 82pt; font-weight: 400; color: ${COBALT}; margin-top: .25in; letter-spacing: -.01em; }
.web { font-size: 30pt; margin-top: .1in; }
</style>
<div class="page"><div class="top">${mark(130)}<div class="name">${B.name}</div></div>
<div class="bar" style="width:3.2in;height:.22in;margin-top:.4in"></div>
<div class="what">Medical, dental and office cleaning</div>
<div class="phone num">${B.phone}</div><div class="web">${B.web}</div></div>`;

// 2. Business cards: 10 per sheet, 3.5 x 2 in (Avery 8371 / 5371 layout, or cut on the guides)
const card = `<div class="card"><div class="c-top">${mark(30)}<div class="c-name">${B.name}</div></div>
<div class="bar" style="width:.9in;height:.06in;margin:.1in 0 .09in"></div>
<div class="c-who">${B.owner}, Owner</div><div class="c-line">${B.line}</div>
<div class="c-contact"><span class="num">${B.phone}</span><span>${B.email}</span><span>${B.web}</span></div></div>`;
const cards = `<style>${base('letter')}
.sheet { width: 8.5in; height: 11in; padding: .5in .75in; display: grid; grid-template-columns: 3.5in 3.5in; grid-auto-rows: 2in; }
.card { padding: .2in .24in; outline: .5pt dashed #c9cfe6; outline-offset: -.25pt; display: flex; flex-direction: column; }
.c-top { display: flex; align-items: center; gap: .1in; }
.c-name { font-size: 17pt; font-weight: 400; color: ${COBALT}; letter-spacing: -.01em; }
.c-who { font-size: 10pt; font-weight: 500; }
.c-line { font-size: 8.5pt; }
.c-contact { margin-top: auto; display: grid; gap: 1pt; font-size: 8.5pt; }
</style><div class="sheet">${card.repeat(10)}</div>`;

// 3. Capability statement
const li = a => a.map(x => `<li>${x}</li>`).join('');
const capability = `<style>${base('letter')}
.page { width: 8.5in; height: 11in; padding: .7in .8in; display: flex; flex-direction: column; }
.head { display: flex; align-items: center; gap: .2in; }
.head .n { font-size: 30pt; font-weight: 300; color: ${COBALT}; letter-spacing: -.01em; }
h1 { font-size: 15pt; font-weight: 500; margin-top: .3in; }
.lead { font-size: 13pt; line-height: 1.45; margin-top: .1in; max-width: 6.3in; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: .25in .5in; margin-top: .35in; }
h2 { font-size: 11pt; font-weight: 500; color: ${COBALT}; margin-bottom: .08in; }
ul { list-style: none; display: grid; gap: .05in; font-size: 10.5pt; line-height: 1.4; }
ul li { padding-left: .18in; position: relative; }
ul li::before { content: ""; position: absolute; left: 0; top: .45em; width: .07in; height: .07in; background: ${COBALT}; }
.foot { margin-top: auto; padding-top: .2in; border-top: 2pt solid ${SUN}; display: flex; justify-content: space-between; font-size: 10.5pt; }
</style>
<div class="page">
<div class="head">${mark(52)}<div class="n">${B.name}</div></div>
<div class="bar" style="width:1.6in;height:.12in;margin-top:.22in"></div>
<h1>Capability statement</h1>
<p class="lead">Owner-operated evening cleaning for medical offices, dental practices, offices and gyms in Brooklyn, Manhattan and Nassau County. We clean after you close and finish before you open.</p>
<div class="grid">
<div><h2>Services</h2><ul>${li(['Medical office cleaning', 'Dental office cleaning', 'Office cleaning', 'Gym and studio cleaning', 'Post-construction cleaning'])}</ul></div>
<div><h2>Service area</h2><ul>${li(['Brooklyn', 'Manhattan', 'Nassau County'])}</ul>
<h2 style="margin-top:.2in">Codes</h2><ul>${li(['NAICS 561720, Janitorial Services'])}</ul></div>
<div><h2>How we work</h2><ul>${li(['The owner cleans or inspects every account', 'A written checklist for every site', 'Color-coded microfiber; EPA-registered disinfectants used per label', 'No handling of sharps or regulated medical waste', 'Keys and alarm codes stored securely', 'Photos after each visit, on request'])}</ul></div>
<div><h2>Terms</h2><ul>${li(['Free 15-minute walkthrough', 'Fixed monthly price in writing within 24 hours', 'Month to month, 30 days\' notice', 'Billed monthly by ACH autopay'])}</ul></div>
</div>
<div class="foot"><span>${B.owner}, Owner</span><span class="num">${B.phone}</span><span>${B.email}</span><span>${B.web}</span></div>
</div>`;

// 4. Color-coded supply labels: 10 per sheet, 2 x 4 in (Avery 5163 / 8163 layout)
const codes = [
  ['#d62828', 'RED', 'Restrooms only', 'Toilets and urinals'],
  ['#e9c400', 'YELLOW', 'Restrooms only', 'Sinks, counters, dispensers'],
  [COBALT, 'BLUE', 'General areas', 'Desks, exam rooms, glass, touch points'],
  ['#1a8f4a', 'GREEN', 'Kitchen and break room', 'Food areas only'],
];
const label = ([c, word, area, detail]) => `<div class="lab"><div class="band" style="background:${c}">${word}</div>
<div class="lt"><div class="la">${area}</div><div class="ld">${detail}</div><div class="lb">${B.name}</div></div></div>`;
const bottle = `<div class="lab"><div class="band" style="background:${INK}">BOTTLE</div>
<div class="lt"><div class="ld" style="line-height:2.1">Product: ____________________<br>Mix / dilution: ______________<br>Hazards: see SDS binder</div><div class="lb">${B.name}</div></div></div>`;
const labels = `<style>${base('letter')}
.sheet { width: 8.5in; height: 11in; padding: .5in .15625in; display: grid; grid-template-columns: 4in 4in; column-gap: .1875in; grid-auto-rows: 2in; }
.lab { display: flex; outline: .5pt dashed #d5d9e8; outline-offset: -.25pt; overflow: hidden; }
.band { width: .62in; color: #fff; font-weight: 500; font-size: 11pt; letter-spacing: .08em; writing-mode: vertical-rl; transform: rotate(180deg); display: grid; place-items: center; }
.lt { padding: .18in .2in; display: flex; flex-direction: column; flex: 1; }
.la { font-size: 18pt; font-weight: 400; line-height: 1.1; }
.ld { font-size: 10.5pt; margin-top: .06in; }
.lb { margin-top: auto; font-size: 8.5pt; color: ${COBALT}; }
</style><div class="sheet">${codes.map(label).join('').repeat(2)}${bottle.repeat(2)}</div>`;

// 5. Nightly site checklist (medical office)
const box = items => items.map(x => `<li><span class="bx"></span>${x}</li>`).join('');
const checklist = `<style>${base('letter')}
.page { width: 8.5in; height: 11in; padding: .55in .7in; display: flex; flex-direction: column; }
.head { display: flex; align-items: center; justify-content: space-between; }
.hn { display: flex; align-items: center; gap: .12in; font-size: 16pt; color: ${COBALT}; }
h1 { font-size: 18pt; font-weight: 400; margin-top: .18in; }
.fields { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: .12in; margin-top: .14in; font-size: 9.5pt; }
.fields div { border-bottom: 1pt solid ${INK}; padding-bottom: .16in; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: .3in .4in; margin-top: .3in; }
h2 { font-size: 12.5pt; font-weight: 500; color: ${COBALT}; margin-bottom: .08in; }
ul { list-style: none; display: grid; gap: .07in; font-size: 11pt; line-height: 1.3; }
li { display: flex; gap: .09in; align-items: flex-start; }
.bx { flex: none; width: .14in; height: .14in; border: 1pt solid ${INK}; margin-top: .02in; }
.never { margin-top: .35in; padding: .14in .18in; background: #fdf7c9; font-size: 11pt; line-height: 1.4; }
.sig { display: grid; grid-template-columns: 1fr 1fr; gap: .4in; margin-top: auto; font-size: 9.5pt; }
.sig div { border-top: 1pt solid ${INK}; padding-top: .05in; }
</style>
<div class="page">
<div class="head"><div class="hn">${mark(26)}${B.name}</div><div style="font-size:9.5pt" class="num">${B.phone}</div></div>
<h1>Nightly cleaning checklist: medical office</h1>
<div class="fields"><div>Site</div><div>Date</div><div>Start</div><div>Finish</div></div>
<div class="cols">
<div><h2>Waiting room and front desk</h2><ul>${box(['Chairs, front desk, pens and clipboards wiped', 'Door handles, light switches, railings disinfected', 'Glass and entry doors spot-cleaned', 'Magazines and brochures straightened'])}</ul></div>
<div><h2>Exam rooms (blue)</h2><ul>${box(['Counters, chairs and exam table surfaces outside the paper', 'Door handles and light switches disinfected', 'Sink and faucet cleaned', 'Paper towels and soap restocked'])}</ul></div>
<div><h2>Restrooms (red and yellow)</h2><ul>${box(['Toilets and urinals disinfected (red)', 'Sinks, counters, mirrors, dispensers (yellow)', 'Paper, soap and liners restocked', 'Floor disinfected last'])}</ul></div>
<div><h2>Break room (green)</h2><ul>${box(['Counters, sink and table', 'Microwave inside and out, fridge front', 'Trash and recycling out'])}</ul></div>
<div><h2>Floors and trash</h2><ul>${box(['All trash and recycling to the building\'s collection area', 'Carpets vacuumed', 'Hard floors damp-mopped, clean head per area'])}</ul></div>
<div><h2>Close-out</h2><ul>${box(['Photos of every room taken', 'Supplies stocked; issues written below', 'Lights off, alarm set, doors locked', 'Keys returned to log'])}</ul></div>
</div>
<div class="never"><b>Never:</b> sharps containers or regulated medical waste, files, drawers, screens or computers, client food, guests on site.</div>
<div style="margin-top:.16in;font-size:9.5pt">Issues or supplies needed:</div>
<div style="border-bottom:1pt solid ${INK};height:.3in"></div><div style="border-bottom:1pt solid ${INK};height:.3in"></div>
<div class="sig" style="margin-top:.45in"><div>Cleaner</div><div>Inspected by</div></div>
</div>`;

const docs = [
  ['1-car-window-sign.pdf', sign, true],
  ['2-business-cards.pdf', cards, false],
  ['3-capability-statement.pdf', capability, false],
  ['4-supply-labels.pdf', labels, false],
  ['5-nightly-checklist.pdf', checklist, false],
];

const browser = await chromium.launch();
const page = await browser.newPage();
for (const [file, body, landscape] of docs) {
  const tmp = join(here, `.tmp-${file}.html`);
  writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"></head><body>${body}</body></html>`);
  await page.goto('file://' + tmp);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: join(here, file), format: 'Letter', landscape, printBackground: true, preferCSSPageSize: true });
  if (process.env.PREVIEW) {
    await page.setViewportSize(landscape ? { width: 1056, height: 816 } : { width: 816, height: 1056 });
    await page.screenshot({ path: join(process.env.PREVIEW, file.replace('.pdf', '.png')) });
  }
  unlinkSync(tmp);
}
await browser.close();
console.log('Wrote', docs.length, 'PDFs to', here);
