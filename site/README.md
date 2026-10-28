# Clean by Morning website

The website for Clean by Morning, evening commercial cleaning in Brooklyn, Manhattan and Nassau County. It's a static site with no dependencies: `build.py` generates every page.

Design: pages open at dusk in the brand cobalt, move through night blues and end in morning white and sun yellow. No prices are shown anywhere on the site; every quote comes after a walkthrough. Section colors are flat steps defined in `static/styles.css` (`.g-dusk` through `.g-day`).

## Edit and build

1. Open `site/build.py` and fill in the settings at the top:
   - `B`: phone, email, form service URL (`form_endpoint`, e.g. Formspree), Google Analytics id, profile links (`same_as`). Everything marked `PLACEHOLDER` must be replaced.
   - `PROOF`: insurance, bond, workers' comp, Google reviews, client names. Each only appears on the site once it's true.
   - `PRICING`: your internal rate model for quoting. It is not shown on the site.
2. Run `python3 site/build.py`.

Output: `site/public/` is the live site to deploy. `site/preview/` is a flat local preview and is not committed.

## Deploy (DreamHost)

The build writes a `.htaccess` into `site/public` that forces `https://www.`, serves the 404 page, and sets caching. Upload the *contents* of `site/public` (not the folder itself) to the domain's web directory, `~/cleanbymorning.com/`.

1. DreamHost panel → Websites → Manage Websites: confirm `cleanbymorning.com` is hosted (Fully Hosted), with the www setting on "Add www" or "Leave it alone".
2. Same page → **HTTPS / SSL certificate**: add the free Let's Encrypt certificate and wait until it shows as active (minutes to an hour). Do this before uploading, because `.htaccess` redirects every visit to https.
3. Upload with either:
   - **Panel**: Websites → Manage Files (the file manager) → open `cleanbymorning.com` → delete DreamHost's placeholder `index.html` → upload `cleanbymorning-site.zip` → extract it there, so `index.html` sits directly in `cleanbymorning.com/`.
   - **SFTP** (FileZilla): host `sftp.dreamhost.com` or your server name, port 22, your website user from Websites → SFTP Users; drag the contents of `site/public` into `cleanbymorning.com/`. Show hidden files so `.htaccess` goes up too.
4. Open `cleanbymorning.com`: it should land on `https://www.cleanbymorning.com/` with the padlock.

To update later: run `python3 site/build.py`, then upload the changed files (or the whole folder) again.

## Email (Cloudflare)

`jamel@cleanbymorning.com` is set up with Cloudflare Email Routing, which forwards what people send to it into your own inbox (for example Gmail). It does not send. To reply from that address, in Gmail go to Settings → Accounts → "Send mail as" → Add another email address, and use a sending service (Gmail's SMTP with an app password, or a service like Resend or Brevo) so replies come from `@cleanbymorning.com`, not your Gmail. Also add SPF and DKIM records for whatever service sends. Keep cold outreach on separate sending domains, not this one.

## Deploy (Cloudflare Pages, free)

1. Cloudflare → Workers & Pages → Create → Pages → Connect to Git → this repo.
2. Build command: empty. Output directory: `site/public`.
3. Add `cleanbymorning.com` as the custom domain.
4. Submit `https://www.cleanbymorning.com/sitemap.xml` in Google Search Console.

## Pages

| URL | Page |
| --- | --- |
| `/` | Home: the promise, services, how we work, areas, FAQ, contact |
| `/services/medical-office-cleaning/` and 4 more | Medical, dental, office, gym and studio, post-construction |
| `/areas/brooklyn/`, `/areas/manhattan/`, `/areas/nassau-county/` | Area pages with their own text and neighborhoods |
| `/guides/` and 3 guides | What affects cleaning costs in NYC, medical office checklist, dental cleaning frequency |
| `/walkthrough/`, `/faq/`, `/about/` | Supporting pages |
| `/one-pager/` | Capability statement for emails and property managers (not indexed) |

Every page has its own title, description, canonical URL and Open Graph tags. Structured data covers LocalBusiness, Service, Article, FAQPage and BreadcrumbList.

## Photos and font

| File | Source |
| --- | --- |
| `img/brooklyn-bridge-lower-manhattan-night.webp` | Oleg Chursin, Unsplash |
| `img/lit-office-windows-at-night.webp` | Vladimir Kudinov, Unsplash |
| `img/morning-at-office-windows.webp` | Charles Forerunner, Unsplash |
| `img/rain-on-window-city-lights.webp` | Riley Briggs, Unsplash |
| `fonts/sentient-*.woff2` | Sentient by Indian Type Foundry, from Fontshare (free for commercial use) |

The photos are atmosphere, not your work. Replace them with your own as you get them.
