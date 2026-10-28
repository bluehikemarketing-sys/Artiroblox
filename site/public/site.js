// Clean by Morning: the price estimator, the walkthrough form, the lit neighborhood names and the section entrances.
(() => {
  const C = window.CBM;
  if (!C) return;
  const P = C.pricing;
  const r5 = x => Math.floor(x / 5 + 0.5) * 5;
  const money = n => '$' + n.toLocaleString('en-US');
  const visit = (kind, sqft, rest) => Math.max(P.min_visit, r5((sqft / P.sqft_per_hour[kind] + rest * P.restroom_hours) * P.hourly));
  const NAMES = { medical: 'Medical office', dental: 'Dental office', office: 'Office', gym: 'Gym or studio', postcon: 'Post-construction' };

  // Estimator
  document.querySelectorAll('[data-estimator]').forEach(form => {
    const fig = form.querySelector('[data-est-figure]');
    const label = form.querySelector('[data-est-label]');
    const detail = form.querySelector('[data-est-detail]');
    const sqftOut = form.querySelector('[data-sqft-out]');
    const cta = form.querySelector('[data-est-cta]');
    const recurring = form.querySelectorAll('[data-recurring]');
    function update() {
      const kind = form.querySelector('[name="kind"]:checked').value;
      const sqft = +form.sqft.value;
      sqftOut.textContent = sqft.toLocaleString('en-US');
      const one = kind === 'postcon';
      recurring.forEach(el => { el.hidden = one; });
      let summary;
      if (one) {
        const total = Math.max(P.postcon_min, r5(sqft * P.postcon_per_sqft));
        label.textContent = 'One-time price';
        fig.textContent = money(total);
        detail.textContent = `${sqft.toLocaleString('en-US')} sq ft, ${Math.round(P.deposit * 100)}% deposit to book.`;
        summary = `${NAMES[kind]}, ${sqft} sq ft, estimate ${money(total)}`;
      } else {
        const nights = +form.querySelector('[name="nights"]:checked').value;
        const rest = +form.restrooms.value;
        const v = visit(kind, sqft, rest);
        const month = r5(v * nights * P.weeks_per_month);
        label.textContent = 'Estimated monthly price';
        fig.textContent = money(month);
        detail.textContent = `About ${money(v)} a visit, ${nights} night${nights > 1 ? 's' : ''} a week.`;
        summary = `${NAMES[kind]}, ${sqft} sq ft, ${rest} restrooms, ${nights} nights a week, estimate ${money(month)}/month`;
      }
      cta.href = C.walkthrough + '?estimate=' + encodeURIComponent(summary);
    }
    form.addEventListener('input', update);
    form.addEventListener('change', update);
    form.addEventListener('submit', e => e.preventDefault());
    update();
  });

  // Walkthrough form: post to a form service when configured, otherwise open a pre-filled email
  document.querySelectorAll('[data-walkthrough]').forEach(form => {
    const msg = form.querySelector('[data-form-msg]');
    try {
      const est = new URLSearchParams(location.search).get('estimate');
      if (est && !form.notes.value) form.notes.value = 'From the estimator: ' + est;
    } catch (e) {}
    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!form.name.value.trim() || !/.+@.+\..+/.test(form.email.value)) { msg.textContent = 'Add your name and a valid email.'; return; }
      const data = Object.fromEntries(new FormData(form).entries());
      if (C.formEndpoint) {
        msg.textContent = 'Sending…';
        try {
          const r = await fetch(C.formEndpoint, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) });
          if (!r.ok) throw new Error(r.status);
          form.reset();
          msg.textContent = "Thanks. We'll reply within one business day with times for the walkthrough.";
          return;
        } catch (err) { msg.textContent = `That didn't send. Email ${C.email} or call ${C.phoneDisplay}.`; return; }
      }
      const body = Object.entries(data).filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join('\n');
      location.href = `mailto:${C.email}?subject=${encodeURIComponent('Walkthrough request: ' + (data.company || data.name))}&body=${encodeURIComponent(body)}`;
      msg.textContent = `Your email app should open with this request. If it doesn't, email ${C.email}.`;
    });
  });

  // Phone action bar: shows when you scroll back up, stays out of the way while you read down
  const bar = document.querySelector('.action-bar');
  if (bar) {
    let lastY = window.scrollY;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      const nearEnd = y + innerHeight > document.documentElement.scrollHeight - 200;
      bar.classList.toggle('show', y < lastY - 4 && y > 300 && !nearEnd);
      lastY = y;
    }, { passive: true });
  }

  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Hero shutter
  requestAnimationFrame(() => document.querySelectorAll('.shutter').forEach(el => el.classList.add('open')));

  // Section entrances and panel pictures
  const targets = document.querySelectorAll('.reveal, .panel');
  if ('IntersectionObserver' in window && !still) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -10% 0px' });
    targets.forEach(t => io.observe(t));
  } else {
    targets.forEach(t => t.classList.add('in'));
  }

  // The hero clock: New York time and where the night's work stands
  document.querySelectorAll('[data-clock]').forEach(el => {
    const fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' });
    const hourOf = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' });
    function tick() {
      const now = new Date();
      const h = +hourOf.format(now);
      let state;
      if (h >= 18 && h < 22) state = "Offices are being cleaned right now.";
      else if (h >= 22 || h < 6) state = 'The clean is done. Offices are locked up for the night.';
      else if (h < 9) state = 'Offices are opening clean this morning.';
      else state = 'We start at 6:00 PM, after you close.';
      el.textContent = `It's ${fmt.format(now)} in New York. ${state}`;
    }
    tick();
    setInterval(tick, 30000);
  });

  // The lit neighborhood name moves through the list
  document.querySelectorAll('[data-names]').forEach(p => {
    const names = [...p.querySelectorAll('a')];
    if (!names.length) return;
    let i = 0;
    names[0].classList.add('lit');
    if (still) return;
    setInterval(() => { names[i].classList.remove('lit'); i = (i + 1) % names.length; names[i].classList.add('lit'); }, 2000);
  });
})();
