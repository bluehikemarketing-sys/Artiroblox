# Clean by Morning website

The website for Clean by Morning, evening commercial cleaning in Brooklyn, Manhattan and Nassau County. It's a static site with no dependencies: `build.py` generates every page.

Design: every page reads as one night. It opens at dusk in the brand cobalt, gets darker through the clean (the "One night at your office" timeline on the home page), and ends in morning white and sun yellow. Section colors are flat steps defined in `static/styles.css` (`.g-dusk` through `.g-day`).

## Edit and build

1. Open `site/build.py` and fill in the settings at the top:
   - `B`: phone, email, form service URL (`form_endpoint`, e.g. Formspree), Google Analytics id, profile links (`same_as`). Everything marked `PLACEHOLDER` must be replaced.
   - `PROOF`: insurance, bond, workers' comp, Google reviews, client names. Each only appears on the site once it's true.
   - `PRICING`: hourly rate, minimum per visit, cleaning speed by space type, post-construction rate. One model drives the estimator, the price lines, the pricing table and the guides.
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

## Deploy (Cloudflare Pages, free)

1. Cloudflare → Workers & Pages → Create → Pages → Connect to Git → this repo.
2. Build command: empty. Output directory: `site/public`.
3. Add `cleanbymorning.com` as the custom domain.
4. Submit `https://www.cleanbymorning.com/sitemap.xml` in Google Search Console.

## Pages

| URL | Page |
| --- | --- |
| `/` | Home: the promise, how it works, price and estimator, neighborhoods, FAQ, contact |
| `/services/medical-office-cleaning/` and 4 more | Medical, dental, office, gym and studio, post-construction |
| `/areas/brooklyn/`, `/areas/manhattan/`, `/areas/nassau-county/` | Area pages with their own text and neighborhoods |
| `/guides/` and 3 guides | Office cleaning cost in NYC, medical office checklist, dental cleaning frequency |
| `/pricing/`, `/walkthrough/`, `/faq/`, `/about/` | Supporting pages |
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
