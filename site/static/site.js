// SunnyMop: instant price, next openings, request by text or email, the Naples photo frame and the first-clean offer.
(() => {
  const C = window.SUNNYMOP;
  if (!C) return;
  const P = C.pricing;
  const r5 = x => Math.floor(x / 5 + 0.5) * 5;
  const NAMES = { standard: 'Standard clean', deep: 'Deep clean', moveout: 'Move-in / move-out clean', airbnb: 'Airbnb turnover' };
  const FREQ = { once: 'one time', weekly: 'weekly', biweekly: 'every 2 weeks', monthly: 'monthly' };

  function price(kind, bed, bath, freq) {
    let v = (P.base + P.per_bed * bed + P.per_bath * bath) * P.mult[kind];
    if (kind === 'standard') v *= 1 - P.freq[freq];
    return Math.max(P.minimum, r5(v));
  }

  const now = new Date();
  const slots = (C.slots && C.slots.length ? C.slots : C.sampleSlots || [])
    .map(s => ({ s, d: new Date(s) })).filter(x => !isNaN(x.d) && x.d > now).slice(0, 4);
  const sample = !(C.slots && C.slots.length) && slots.length > 0;
  const fmt = d => d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) + ', ' +
    d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

  function send(subject, body) {
    if (C.bookingUrl) { window.location.href = C.bookingUrl; return; }
    const sms = 'sms:' + C.phone + '?&body=' + encodeURIComponent(body);
    const mail = 'mailto:' + C.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    const mobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
    window.location.href = mobile ? sms : mail;
  }

  document.querySelectorAll('[data-quote]').forEach((form, n) => {
    const total = form.querySelector('[data-total]');
    const per = form.querySelector('[data-per]');
    const freqField = form.querySelector('[data-freq-field]');
    const zip = form.querySelector('[name="zip"]');
    const zipMsg = form.querySelector('[data-zip-msg]');
    const slotBox = form.querySelector('[data-slots]');
    const slotEmpty = form.querySelector('[data-slots-empty]');
    const note = form.querySelector('[data-quote-note]');

    // Give each form's controls unique ids when a page has more than one.
    if (n > 0) form.querySelectorAll('[id]').forEach(el => {
      const old = el.id; el.id = old + '-' + n;
      const lab = form.querySelector(`label[for="${old}"]`); if (lab) lab.htmlFor = el.id;
    });

    if (slots.length) {
      slotEmpty.hidden = true;
      slotBox.innerHTML = slots.map((x, i) => `<label class="chip"><input type="radio" name="slot" value="${x.s}"${i === 0 ? ' checked' : ''}><span>${fmt(x.d)}</span></label>`).join('');
      if (sample) slotBox.insertAdjacentHTML('afterend', '<p class="slots-empty">Sample openings shown in this preview.</p>');
    }

    function state() {
      const kind = form.service.value;
      const bed = +form.beds.value, bath = +form.baths.value;
      const freq = (form.querySelector('[name="freq"]:checked') || {}).value || 'once';
      const adds = [...form.querySelectorAll('[name="addon"]:checked')].map(i => P.addons.find(a => a[0] === i.value));
      return { kind, bed, bath, freq: kind === 'standard' ? freq : 'once', adds };
    }
    function update() {
      const s = state();
      freqField.hidden = s.kind !== 'standard';
      const t = price(s.kind, s.bed, s.bath, s.freq) + s.adds.reduce((a, x) => a + x[2], 0);
      total.textContent = '$' + t;
      per.textContent = s.kind === 'airbnb' ? 'per turnover' : (s.freq !== 'once' ? 'per visit' : 'per clean');
      return t;
    }
    function checkZip() {
      const z = zip.value.trim();
      if (!z) { zipMsg.textContent = ''; return true; }
      if (!/^\d{5}$/.test(z)) { zipMsg.textContent = 'Enter a 5-digit zip code.'; return false; }
      if (!C.zips.includes(z)) { zipMsg.textContent = `We don't clean in ${z} yet. Text us and we'll tell you if we can make it work.`; return false; }
      zipMsg.textContent = ''; return true;
    }
    form.addEventListener('input', update);
    form.addEventListener('change', update);
    zip.addEventListener('blur', checkZip);
    form.addEventListener('submit', e => {
      e.preventDefault();
      checkZip();
      const s = state(); const t = update();
      const slot = form.querySelector('[name="slot"]:checked');
      const lines = [
        `Hi SunnyMop, I'd like to book: ${NAMES[s.kind]}${s.kind === 'standard' ? ' (' + FREQ[s.freq] + ')' : ''}`,
        `${s.bed} bed, ${s.bath} bath${zip.value ? ', zip ' + zip.value.trim() : ''}`,
        s.adds.length ? 'Add-ons: ' + s.adds.map(a => a[1]).join(', ') : '',
        `Price shown: $${t}`,
        slot ? 'Opening: ' + fmt(new Date(slot.value)) : 'Next opening, please.'
      ].filter(Boolean);
      send('Cleaning request', lines.join('\n'));
      note.textContent = `Your text or email app should open with this request. If it doesn't, text ${C.phoneDisplay}.`;
    });
    update();
  });

  // The Naples frame: tap to show the next photo
  document.querySelectorAll('[data-frame]').forEach(btn => {
    const imgs = [...btn.querySelectorAll('img')];
    const cap = btn.parentNode.querySelector('[data-frame-caption]');
    let i = 0;
    btn.addEventListener('click', () => {
      imgs[i].classList.remove('on');
      i = (i + 1) % imgs.length;
      imgs[i].classList.add('on');
      if (cap) cap.textContent = imgs[i].dataset.caption || '';
    });
  });

  // First-clean offer
  document.querySelectorAll('[data-offer]').forEach(form => {
    const msg = form.querySelector('[data-offer-msg]');
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.name.value.trim() || !form.phone.value.trim()) { msg.textContent = 'Add your name and mobile number.'; return; }
      const body = `Hi SunnyMop, I'd like my first-clean offer.\nName: ${form.name.value.trim()}\nMobile: ${form.phone.value.trim()}` +
        (form.zip.value ? `\nZip: ${form.zip.value.trim()}` : '') + `\nService: ${form.service.value}`;
      send('First-clean offer', body);
      msg.textContent = `Your text or email app should open with this message. If it doesn't, text ${C.phoneDisplay}.`;
    });
  });
})();
