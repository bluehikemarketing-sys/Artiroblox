# Clean by Morning website

The website for Clean by Morning, evening commercial cleaning in Brooklyn, Manhattan and Nassau County. It's a static site with no dependencies: `build.py` generates every page.

## Edit and build

1. Open `site/build.py` and fill in the settings at the top:
   - `B`: phone, email, form service URL (`form_endpoint`, e.g. Formspree), Google Analytics id, profile links (`same_as`). Everything marked `PLACEHOLDER` must be replaced.
   - `PROOF`: insurance, bond, workers' comp, Google reviews, client names. Each only appears on the site once it's true.
   - `PRICING`: hourly rate, minimum per visit, cleaning speed by space type, post-construction rate. One model drives the estimator, the price lines, the pricing table and the guides.
2. Run `python3 site/build.py`.

Output: `site/public/` is the live site to deploy. `site/preview/` is a flat local preview and is not committed.

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
