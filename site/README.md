# Sea Grape Home Cleaning website

A static site for a house cleaning business in Naples, FL. There are no dependencies: `build.py` generates every page from one file.

## Edit and build

1. Open `site/build.py` and replace every `PLACEHOLDER` value in `BUSINESS`: domain, phone, email and booking link.
2. Edit the copy, prices (`BASE_FIXED`, `PER_BED`, `PER_BATH`, `MULT`) or areas in the same file.
3. Run `python3 site/build.py`.

The build writes:

| Output | What it is |
| --- | --- |
| `site/public/` | The live website, which is the folder you deploy |
| `site/preview/` | A local preview with relative links (not committed) |
| `brand/BRAND.md`, `brand/*.svg` | The brand kit |
| `docs/seo-and-channels-checklist.md` | The SEO and marketing checklist |

## Deploy (Cloudflare Pages, free)

1. In Cloudflare, go to Workers & Pages, then Create, then Pages, then Connect to Git, and pick this repo.
2. Leave the build command empty and set the output directory to `site/public`.
3. Add your custom domain. HTTPS is automatic.
4. Submit `https://your-domain/sitemap.xml` in Google Search Console.

Cloudflare Pages serves `/pricing` from `pricing.html`, which matches the canonical URLs the build writes.

## Pages

- Home: Naples house cleaning
- 5 service pages: recurring, deep, move-in/move-out, seasonal home, vacation rental
- 3 area pages: Marco Island, Bonita Springs, Estero (the home page covers Naples)
- Pricing, FAQ, About, and Book (an instant price estimator that links to your booking app)
- 404 page, `sitemap.xml`, `robots.txt`

Each page has a title, description and canonical URL. The structured data covers LocalBusiness, Service, FAQPage and BreadcrumbList.
