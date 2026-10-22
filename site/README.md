# SunnyMop website

The website for SunnyMop, a house cleaning company in Naples, FL. It's a static site with no dependencies: `build.py` generates every page from one file.

## Edit and build

1. Open `site/build.py` and fill in the settings at the top:
   - `B`: domain, phone, email, booking link, Google Analytics id and first-clean offer. Everything marked `PLACEHOLDER` must be replaced.
   - `PROOF`: insurance, bond, background checks and Google reviews. A badge or rating only appears once its setting is true or filled in.
   - `BEFORE_AFTER`: your own before-and-after photo pairs. The gallery stays hidden until you add one.
   - `OPEN_SLOTS`: openings you can really take. Past ones hide automatically.
   - `PRICING`: one formula used everywhere: the quote tool, the price tiles, the pricing table and the schema.
2. Run `python3 site/build.py`.

The build writes:

| Output | What it is |
| --- | --- |
| `site/public/` | The live website; this is the folder you deploy |
| `site/preview/` | A flat preview with relative links (not committed) |
| `brand/` | Brand notes, the wordmark and the sun mark |
| `docs/launch-checklist.md` | What to do before and after launch |

## Deploy (Cloudflare Pages, free)

1. In Cloudflare, go to Workers & Pages, then Create, then Pages, then Connect to Git, and pick this repo.
2. Leave the build command empty and set the output directory to `site/public`.
3. Add your custom domain.
4. Submit `https://your-domain/sitemap.xml` in Google Search Console.

## Pages

| URL | Page |
| --- | --- |
| `/` | Home: instant price and next openings, what's included, prices, how it works, services, areas, FAQ, first-clean offer |
| `/services/<service>/naples-fl/` | Standard, deep, move-in/move-out, Airbnb and recurring cleaning |
| `/locations/<area>/` | Old Naples, Park Shore, Pelican Bay, Vanderbilt Beach, North Naples, East Naples, each with its own text |
| `/pricing/`, `/faq/`, `/about/`, `/book/`, `/contact/` | Supporting pages |

Every page has its own title, meta description, canonical URL and Open Graph tags. The structured data covers LocalBusiness, Service, FAQPage and BreadcrumbList.

## Booking

Until you choose booking software, "Request this clean" opens a pre-filled text (on phones) or email (on computers) with the price, home size and chosen opening. Once you pick a booking tool, set `booking_url` and the button goes there instead.

## Photos

| File | Source | Licence |
| --- | --- | --- |
| `naples-pier-*.webp` (3) | MJJR, Wikimedia Commons | CC BY 4.0, credited in the footer |
| `gulf-surf-on-sand.webp`, `palms-on-the-beach.webp`, `wide-beach-with-palms.webp` | Sarah Bürvenich, Florian Klauer, Paula Borowska (Unsplash) | Unsplash licence |

The beach photos are not Naples and are used only as atmosphere. Replace them with your own photos when you can.
