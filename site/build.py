#!/usr/bin/env python3
"""Build the SunnyMop website, brand kit and launch checklist.

Usage:  python3 site/build.py

Writes:
  site/public/   the live website (deploy this folder to Cloudflare Pages)
  site/preview/  a flat preview copy with relative links (not committed)
  brand/ and docs/

Everything marked PLACEHOLDER must be replaced before launch. Proof (insurance, reviews, before-and-after
photos) only appears once the matching setting below is filled in with something real.
"""
import html
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

# ---------------------------------------------------------------------------
# Business settings
# ---------------------------------------------------------------------------
B = {
    "name": "SunnyMop",
    "domain": "https://www.sunnymop.com",          # PLACEHOLDER: buy the domain, then set it here
    "phone_display": "(239) 555-0100",              # PLACEHOLDER: your Quo number
    "phone_e164": "+12395550100",                   # PLACEHOLDER
    "email": "hello@sunnymop.com",                  # PLACEHOLDER
    "hours": "Mon–Sat, 8 AM–6 PM",
    "hours_schema": ["Mo-Sa 08:00-18:00"],
    "city": "Naples", "state": "FL",
    "booking_url": "",          # your booking app's page once you have one (ZenMaid, Jobber, ...); empty = text/email request
    "ga4_id": "",               # Google Analytics 4 measurement id, e.g. "G-XXXXXXX"; empty = no analytics
    "first_clean_off": 25,      # PLACEHOLDER amount: dollars off the first clean
    "year": 2026,
    "same_as": [],              # Google Business Profile, Facebook, Instagram... once they exist
}

# Proof. Fill in only what is true today; empty or False keeps it off the site.
PROOF = {
    "insured": False,               # True once general liability insurance is bound
    "bonded": False,                # True once a janitorial bond is in place
    "background_checked": False,    # True once every cleaner has passed a background check
    "review_count": 0,              # your real Google review count
    "rating": None,                 # your real Google rating, e.g. 4.9
    "google_reviews_url": "",       # link to your Google reviews
}

# Real SunnyMop job photos, same angle before and after. Put files in site/static/img/ and list them here:
# {"before": "deep-cleaning-oven-before-naples.webp", "after": "deep-cleaning-oven-after-naples.webp",
#  "alt": "Oven before and after deep cleaning in Naples, FL", "service": "deep-cleaning"}
BEFORE_AFTER = []

# Openings you can really take. ISO date-times in Naples local time, e.g. "2026-10-27T09:00".
# Past ones are hidden automatically. Empty = the page asks people to text for the next opening.
OPEN_SLOTS = []
# Shown in the preview build only, labelled as samples.
SAMPLE_SLOTS = ["2026-10-27T09:00", "2026-10-27T13:00", "2026-10-28T09:00", "2026-10-29T13:00"]

ZIPS = ["34102", "34103", "34104", "34105", "34108", "34109", "34110", "34112", "34113", "34114", "34116", "34117", "34119", "34120"]

# ---------------------------------------------------------------------------
# Pricing: one formula for the quote, the tiles, the tables and the schema
# ---------------------------------------------------------------------------
PRICING = {
    # Matched to the Naples average (HomeAdvisor: $148 a clean, typical $119–$203): a 2-bed, 2-bath clean is $150.
    "base": 70, "per_bed": 25, "per_bath": 15,      # one-time standard clean
    "mult": {"standard": 1.0, "deep": 1.5, "moveout": 1.6, "airbnb": 0.6},
    "freq": {"once": 0.0, "weekly": 0.20, "biweekly": 0.15, "monthly": 0.10},  # recurring discounts, standard only
    "minimum": 110,
    "addons": [["oven", "Inside the oven", 35], ["fridge", "Inside the fridge", 35], ["cabinets", "Inside cabinets", 45],
               ["baseboards", "Baseboards (included in deep)", 35], ["windows", "Interior windows", 45], ["laundry", "Laundry, wash and fold", 25]],
}


def r5(x):
    return int(math.floor(x / 5 + 0.5) * 5)


def price(kind, bed, bath, freq="once"):
    p = PRICING
    v = (p["base"] + p["per_bed"] * bed + p["per_bath"] * bath) * p["mult"][kind]
    if kind == "standard":
        v *= 1 - p["freq"][freq]
    return max(p["minimum"], r5(v))


SERVICES = [
    {"key": "standard", "slug": "standard-cleaning", "name": "Standard cleaning", "kind": "standard",
     "h1": "Standard cleaning in Naples, FL", "short": "Kitchen, bathrooms, floors and dusting, done to a checklist.",
     "lead": "A full top-to-bottom clean of the rooms you live in: kitchen, bathrooms, bedrooms and living areas, done to the same checklist every visit.",
     "included": ["Kitchen counters, backsplash, sink and stovetop degreased", "Outside of fridge, oven and dishwasher; inside the microwave",
                  "Bathrooms: shower, tub, toilet, sink, mirrors and glass", "Dusting of every reachable surface, fans and light switches",
                  "Floors vacuumed and mopped, edges included", "Beds made, trash out, lanai furniture wiped"],
     "good_for": "Homes that are lived in and kept up, or a one-time reset before guests arrive.",
     "faq": [("How long does a standard clean take?", "About 3 hours for a 3-bedroom, 2-bathroom home with one cleaner. Larger homes get two cleaners."),
             ("Is standard cleaning enough for a first visit?", "If the home was cleaned professionally in the last month, yes. Otherwise we recommend a deep clean first so later visits hold that level."),
             ("Can I add the inside of the oven or fridge?", "Yes. Pick add-ons in the price tool; each is priced upfront.")]},
    {"key": "deep", "slug": "deep-cleaning", "name": "Deep cleaning", "kind": "deep",
     "h1": "Deep cleaning in Naples, FL", "short": "Baseboards, grout, cabinet fronts and the build-up a standard clean skips.",
     "lead": "Everything in a standard clean, plus the build-up a regular clean doesn't reach: baseboards, door frames, cabinet fronts, grout and hard-water spots.",
     "included": ["Everything in a standard clean", "Baseboards, door frames, vents and light fixtures", "Cabinet fronts and handles wiped down",
                  "Grout scrubbed; hard-water spots on glass and fixtures", "Stovetop grates and burner caps degreased", "Window sills and tracks"],
     "good_for": "First visits, homes that haven't had a professional clean in a while, and spring or holiday resets.",
     "faq": [("What's the difference between standard and deep cleaning?", "A deep clean adds the detail work: baseboards, door frames, cabinet fronts, grout, hard-water spots and stovetop grates. It takes about one and a half times as long."),
             ("How long does a deep clean take?", "About 5 hours for a 3-bedroom, 2-bathroom home with one cleaner, or less with two."),
             ("Is the inside of the oven included?", "It's an add-on, priced upfront in the price tool, because ovens vary a lot."),
             ("Do I need to move things before you arrive?", "Clear counters and floors where you can. We don't move heavy furniture.")]},
    {"key": "moveout", "slug": "move-out-cleaning", "name": "Move-in and move-out cleaning", "kind": "moveout",
     "h1": "Move-out cleaning in Naples, FL", "short": "Empty-home cleans timed to your closing or lease end.",
     "lead": "Empty-home cleaning for move-ins and move-outs, timed to your closing or lease end, with finish photos you can send to the landlord, buyer or property manager.",
     "included": ["Inside every cabinet, drawer and closet", "Inside the fridge, oven and microwave", "Kitchen and bathrooms scrubbed and disinfected",
                  "Baseboards, door frames, vents and switches", "Floors vacuumed and mopped throughout", "Finish photos sent the same day"],
     "good_for": "Tenants getting a deposit back, sellers before closing, buyers before moving in, and realtors and property managers between occupants.",
     "faq": [("Does the home need to be empty?", "Yes, or nearly. Furniture left in place limits what we can reach, especially floors and closets."),
             ("Will this get my deposit back?", "We clean to the standard most Naples landlords inspect for, and send photos you can share. The deposit decision is your landlord's."),
             ("Do you work with realtors and property managers?", "Yes. We work from lockboxes, schedule around showings and closings, and send photos for your file."),
             ("Do you clean before a move-in too?", "Yes. The same service works for a home you're moving into.")]},
    {"key": "airbnb", "slug": "airbnb-cleaning", "name": "Airbnb and vacation rental cleaning", "kind": "airbnb",
     "h1": "Airbnb cleaning in Naples, FL", "short": "Turnovers between check-out and check-in, with photos for the host.",
     "lead": "Turnover cleaning between check-out and check-in for Airbnb and VRBO homes in Naples, with photos of anything broken, missing or running low.",
     "included": ["Full turnover clean of kitchen, bathrooms and floors", "Beds made with the host's linens", "Trash out, dishes done, surfaces reset",
                  "Restock check against your list", "Photos of damage or missing items sent to you", "Same-day turnovers between check-out and check-in"],
     "good_for": "Hosts, co-hosts and rental managers who need dependable turnovers on a schedule.",
     "faq": [("Do you provide linens?", "We use the host's linens and can add laundry to each turnover."),
             ("Can you work from my booking calendar?", "Yes. Share your calendar or a schedule and we'll book turnovers around check-outs."),
             ("What if a guest leaves damage?", "We photograph it and text you before we leave, so you can file with the platform.")]},
    {"key": "recurring", "slug": "recurring-cleaning", "name": "Recurring cleaning", "kind": "standard",
     "h1": "Recurring house cleaning in Naples, FL", "short": "Weekly, every two weeks or monthly, with the same cleaner when possible.",
     "lead": "Standard cleaning on a schedule: weekly, every two weeks or monthly. The more often we come, the less each visit costs.",
     "included": ["Everything in a standard clean, every visit", "Weekly saves 20%, every two weeks saves 15%, monthly saves 10%",
                  "Request the same cleaner each visit", "Skip or move a visit with 48 hours' notice", "First visit is a deep clean, so every visit after holds that level", "Pay after each clean"],
     "good_for": "Busy households, retirees and anyone who wants the house kept up without thinking about it.",
     "faq": [("How often should I book?", "Every two weeks suits most homes. Weekly works best with kids or pets. Monthly keeps a quiet home in shape."),
             ("Can I keep the same cleaner?", "Yes, you can request the same cleaner each visit and we'll match you whenever possible."),
             ("Can I pause for the summer?", "Yes. Tell us 48 hours before your next visit.")]},
]
SVC = {s["key"]: s for s in SERVICES}

LOCATIONS = [
    {"slug": "old-naples", "name": "Old Naples", "zips": ["34102"],
     "lead": "House cleaning in Naples' historic district, from beach cottages off Gulf Shore Boulevard to newer homes a few blocks from Fifth Avenue South.",
     "body": ["Old Naples runs from the Naples Pier to the shops of Fifth Avenue South and Third Street South. Homes here range from older cottages to large new builds, and many sit a short walk from the beach.",
              "Beach sand is the constant. Our checklist for homes near the Gulf includes entry floors, sliding-door tracks and lanai furniture on every visit.",
              "Many Old Naples owners are away part of the year. We clean from lockbox or keypad access and text finish photos when we're done."]},
    {"slug": "park-shore", "name": "Park Shore", "zips": ["34103"],
     "lead": "Condo and home cleaning in Park Shore, between Gulf Shore Boulevard's high-rises and Venetian Bay.",
     "body": ["Park Shore mixes Gulf-front high-rise condos with single-family homes along the waterways off Venetian Bay.",
              "For condo buildings, we follow the association's rules on service hours, parking and elevators, and send any vendor paperwork before the first visit.",
              "Condos here are often furnished rentals or second homes. We clean between guests or before owners arrive, with photos for anyone who isn't there."]},
    {"slug": "pelican-bay", "name": "Pelican Bay", "zips": ["34108"],
     "lead": "House and condo cleaning in Pelican Bay, the planned community between US 41 and the Gulf.",
     "body": ["Pelican Bay is a planned community of high-rise condos, villas and single-family homes, with private beach facilities reached by boardwalks.",
              "Gated entries mean access needs to be set up ahead of time. We confirm gate and building access when you book, so your cleaner isn't turned away.",
              "Owners here often book a deep clean when they arrive for the season, then cleans every two weeks until they leave."]},
    {"slug": "vanderbilt-beach", "name": "Vanderbilt Beach", "zips": ["34108"],
     "lead": "Cleaning for beachfront condos and homes around Vanderbilt Beach Road.",
     "body": ["Around Vanderbilt Beach Road you'll find Gulf-front condo towers, older single-family homes and short-term rentals within walking distance of the sand.",
              "Short-term rentals here need fast, dependable turnovers. We clean between check-out and check-in and photograph anything a guest broke or used up.",
              "For year-round homes, a clean every two weeks keeps sand and salt film under control."]},
    {"slug": "north-naples", "name": "North Naples", "zips": ["34109", "34110", "34119"],
     "lead": "House cleaning across North Naples, from Naples Park to the gated communities off Immokalee Road.",
     "body": ["North Naples covers established neighborhoods like Naples Park as well as newer gated communities east of I-75 and around Mercato.",
              "Most homes here are single-family houses with three or more bedrooms, where a clean every two weeks is the usual rhythm.",
              "Moving within North Naples? Book a move-out clean for the old place and a move-in clean for the new one."]},
    {"slug": "east-naples", "name": "East Naples", "zips": ["34112", "34113", "34114"],
     "lead": "House cleaning in East Naples, from the neighborhoods near Naples Bay to Lely and the communities along Collier Boulevard.",
     "body": ["East Naples stretches from the neighborhoods near Naples Bay and the Naples Botanical Garden out to golf communities around Lely and Collier Boulevard.",
              "Homes here are mostly single-family houses and villas. Many families book a deep clean first, then a recurring plan.",
              "Rentals turn over often in East Naples. Our move-out clean covers the inside of every cabinet and appliance, with photos for the landlord."]},
]

PHOTOS = {
    "pier_sea_grapes": {"file": "naples-pier-beach-sea-grapes.webp", "w": 960, "h": 699, "alt": "Naples Pier seen from the beach past sea grape bushes", "caption": "Naples Pier from the beach, Old Naples"},
    "pier_walkers": {"file": "naples-pier-walkers.webp", "w": 1600, "h": 1040, "alt": "People walking under the wooden Naples Pier", "caption": "Under the Naples Pier"},
    "pier_plaque": {"file": "naples-pier-historic-plaque.webp", "w": 1200, "h": 900, "alt": "Historic marker for the Naples Pier, built in 1888", "caption": "The Naples Pier marker: built in 1888"},
    "surf": {"file": "gulf-surf-on-sand.webp", "w": 1200, "h": 750, "alt": "Surf breaking on golden sand", "caption": ""},
    "palms": {"file": "palms-on-the-beach.webp", "w": 1600, "h": 1000, "alt": "Palm trees on a bright beach", "caption": ""},
    "wide_beach": {"file": "wide-beach-with-palms.webp", "w": 1600, "h": 1000, "alt": "A wide sandy beach lined with palms", "caption": ""},
}
CREDITS = ('Naples Pier photos: <a href="https://commons.wikimedia.org/wiki/File:Naples_Pier_R04.jpg">MJJR</a>, '
           '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, via Wikimedia Commons. '
           'Beach photos: Sarah Bürvenich, Florian Klauer and Paula Borowska, via Unsplash.')

FAQ = [
    ("How much does house cleaning cost in Naples?", f"Our standard clean starts at ${price('standard', 1, 1)} for a 1-bedroom, 1-bathroom home, and a 3-bedroom, 2-bathroom home is ${price('standard', 3, 2)}. Recurring plans save up to 20%. The price tool shows your exact price before you book."),
    ("Do I need to be home during the clean?", "No. Many clients are at work or out of town. Leave a key in a lockbox or give us a door or gate code, and we'll text you when we're done."),
    ("Do you bring cleaning supplies?", "Yes, every time. If you prefer a product, leave it out and we'll use it."),
    ("What's your guarantee?", "If something isn't right, tell us within 48 hours and we'll come back and re-clean it free. If it's still not right after that, we refund the clean."),
    ("How do I pay?", "You pay after the clean is finished, never before."),
    ("Can I get the same cleaner every time?", "Yes. Ask for the same cleaner and we'll match you whenever possible."),
    ("What's the difference between standard and deep cleaning?", "A deep clean adds detail work a standard clean skips: baseboards, door frames, cabinet fronts, grout and hard-water spots."),
    ("Do you clean Airbnbs and vacation rentals?", "Yes. We do turnovers between guests and photograph anything broken, missing or running low."),
    ("What's your cancellation policy?", "Move or cancel free with 48 hours' notice."),
    ("Which areas do you serve?", "All of Naples, including Old Naples, Park Shore, Pelican Bay, Vanderbilt Beach, North Naples and East Naples."),
]

E = html.escape


# ---------------------------------------------------------------------------
# Page model: live site uses nested clean URLs, preview uses flat files
# ---------------------------------------------------------------------------
def live_path(key):
    if key == "index":
        return "/"
    if key.startswith("svc:"):
        return f"/services/{SVC[key[4:]]['slug']}/naples-fl/"
    if key.startswith("loc:"):
        return f"/locations/{key[4:]}/"
    return f"/{key}/"


def live_file(key):
    if key == "404":
        return "404.html"
    p = live_path(key).strip("/")
    return (p + "/index.html") if p else "index.html"


def preview_file(key):
    if key == "index":
        return "home.html"
    return key.replace(":", "-") + ".html"


class Ctx:
    def __init__(self, preview):
        self.preview = preview

    def href(self, key, anchor=""):
        return (preview_file(key) if self.preview else live_path(key)) + anchor

    def canonical(self, key):
        return B["domain"] + live_path(key)

    def asset(self, name):
        return name if self.preview else "/" + name

    def img(self, key, cls="", sizes="", lazy=True, extra=""):
        p = PHOTOS[key]
        return (f'<img class="{cls}" src="{self.asset("img/" + p["file"])}" alt="{E(p["alt"])}" width="{p["w"]}" height="{p["h"]}"'
                f'{" loading=\"lazy\"" if lazy else ""} decoding="async"{extra}>')


def wordmark(tag="span", cls="wordmark", href=None):
    inner = 'sunnym<span class="sun-o" aria-hidden="true"></span>p'
    if href:
        return f'<a class="{cls}" href="{href}" aria-label="SunnyMop home">{inner}</a>'
    return f'<{tag} class="{cls}" aria-label="SunnyMop">{inner}</{tag}>'


def jsonld(o):
    return f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>'


def business_schema():
    s = {"@context": "https://schema.org", "@type": "LocalBusiness",
         "@id": B["domain"] + "/#business", "name": B["name"], "url": B["domain"] + "/",
         "telephone": B["phone_e164"], "email": B["email"], "priceRange": "$$$",
         "description": "Premium house cleaning in Naples, Florida: standard, deep, move-in and move-out, Airbnb and recurring cleaning.",
         "areaServed": {"@type": "City", "name": "Naples, FL"}, "openingHours": B["hours_schema"],
         "image": B["domain"] + "/img/" + PHOTOS["pier_sea_grapes"]["file"], "sameAs": B["same_as"]}
    if PROOF["review_count"] and PROOF["rating"]:
        s["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": PROOF["rating"], "reviewCount": PROOF["review_count"]}
    return s


def crumbs_schema(ctx, trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": ctx.canonical(k)} for i, (k, n) in enumerate(trail)]}


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def promises():
    items = ["Prices shown upfront", "Free re-clean within 48 hours", "Pay after the clean"]
    if PROOF["insured"]:
        items.insert(0, "Insured")
    if PROOF["bonded"]:
        items.insert(0, "Bonded")
    if PROOF["background_checked"]:
        items.insert(0, "Background-checked cleaners")
    if PROOF["review_count"] and PROOF["rating"]:
        items.insert(0, f'{PROOF["rating"]} stars from {PROOF["review_count"]} Google reviews')
    return '<ul class="promise">' + "".join(f'<li><span class="dot" aria-hidden="true"></span>{E(t)}</li>' for t in items) + "</ul>"


NAV = [("svc:standard", "Services"), ("index#areas", "Areas"), ("pricing", "Pricing"), ("faq", "FAQ"), ("contact", "Contact")]


def nav_href(ctx, k):
    if "#" in k:
        base, anc = k.split("#")
        return ctx.href(base, "#" + anc)
    if k == "svc:standard":
        return ctx.href("index", "#services")
    return ctx.href(k)


def header(ctx, active):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{nav_href(ctx, k)}"{cur if k == active else ""}>{E(n)}</a>' for k, n in NAV)
    menu = "".join(f'<a href="{nav_href(ctx, k)}">{E(n)}</a>' for k, n in NAV)
    bar = ""
    if ctx.preview:
        bar = ('<div class="preview-bar"><div class="wrap"><strong>Preview</strong><span>Phone, email, domain, offer amount and openings are placeholders.</span>'
               '<a href="brand-kit.html">Brand kit</a><a href="checklist.html">Launch checklist</a><a href="home.html">Home</a></div></div>')
    return f'''{bar}<header class="site-header"><div class="wrap">
{wordmark(href=ctx.href("index"))}
<nav class="nav" aria-label="Main">{links}</nav>
<a class="btn btn-sun header-cta" href="{ctx.href("book")}">Get my price</a>
<details class="menu"><summary>Menu</summary><div class="menu-panel">{menu}<a href="{ctx.href("book")}">Get my price</a></div></details>
</div></header>'''


def action_bar(ctx):
    return (f'<div class="action-bar"><a class="btn btn-plain" href="sms:{B["phone_e164"]}">Text us</a>'
            f'<a class="btn btn-sun" href="{ctx.href("book")}">Get my price</a></div>')


def footer(ctx):
    svc = "".join(f'<li><a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a></li>' for s in SERVICES)
    loc = "".join(f'<li><a href="{ctx.href("loc:" + l["slug"])}">{E(l["name"])}</a></li>' for l in LOCATIONS)
    co = "".join(f'<li><a href="{ctx.href(k)}">{n}</a></li>' for k, n in [("pricing", "Pricing"), ("faq", "FAQ"), ("about", "About"), ("contact", "Contact"), ("book", "Book a clean")])
    social = "".join(f'<li><a href="{E(u)}">{E(u.split("//")[-1].split("/")[0])}</a></li>' for u in B["same_as"])
    return f'''<footer class="site-footer"><div class="wrap">
<p class="big-mark" aria-hidden="true">sunnym<span class="sun-o"></span>p</p>
<div class="foot-cols">
<div><h2>Services</h2><ul>{svc}</ul></div>
<div><h2>Naples areas</h2><ul>{loc}</ul></div>
<div><h2>Company</h2><ul>{co}</ul></div>
{f'<div><h2>Find us</h2><ul>{social}</ul></div>' if social else ""}
<div><h2>SunnyMop, Naples, FL</h2><ul><li>Call or text <span class="num">{E(B["phone_display"])}</span></li><li>{E(B["email"])}</li><li>{E(B["hours"])}</li><li>All Naples zip codes</li></ul></div>
</div>
<p class="credits">{CREDITS}</p>
<div class="foot-last"><span>© {B["year"]} SunnyMop. House cleaning in Naples, Florida.</span><a class="btn btn-ink" href="{ctx.href("book")}">Get my price</a></div>
</div></footer>'''


def page(ctx, key, title, desc, body, active=None, schema=(), noindex=False, wrapper=True, scripts=()):
    canon = ctx.canonical(key)
    ga = ""
    if B["ga4_id"] and not ctx.preview:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={B["ga4_id"]}"></script>'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{B["ga4_id"]}");</script>')
    head = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ""}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:site_name" content="SunnyMop">
<meta property="og:image" content="{B["domain"]}/img/{PHOTOS["pier_sea_grapes"]["file"]}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffc61a">
<link rel="icon" href="{ctx.asset("favicon.svg")}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;600;800&display=swap">
<link rel="stylesheet" href="{ctx.asset("styles.css")}">
{ga}{"".join(jsonld(s) for s in schema)}'''
    js = "".join(f'<script src="{ctx.asset(s)}" defer></script>' for s in scripts)
    content = f'''{header(ctx, active)}
<main id="main">
{body}
</main>
{footer(ctx)}
{action_bar(ctx)}
{js}'''
    if not wrapper:
        return head + "\n" + content + "\n"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body>
{content}
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
def quote_widget(ctx, preset="standard", heading="Your price"):
    opts = [("standard", "Standard"), ("deep", "Deep"), ("moveout", "Move-in / move-out"), ("airbnb", "Airbnb turnover")]
    sel = "".join(f'<option value="{k}"{" selected" if k == preset else ""}>{n}</option>' for k, n in opts)
    beds = "".join(f'<option value="{n}"{" selected" if n == 3 else ""}>{n} bed</option>' for n in range(1, 7))
    baths = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n} bath</option>' for n in range(1, 6))
    freqs = "".join(f'<label class="chip"><input type="radio" name="freq" id="freq-{k}" value="{k}"{" checked" if k == ("biweekly" if preset == "recurring" else "once") else ""}><span>{n}</span></label>'
                    for k, n in [("once", "One time"), ("weekly", "Weekly −20%"), ("biweekly", "Every 2 weeks −15%"), ("monthly", "Monthly −10%")])
    adds = "".join(f'<label class="chip"><input type="checkbox" name="addon" id="add-{k}" value="{k}"><span>{E(n.split(" (")[0])} +${p}</span></label>' for k, n, p in PRICING["addons"])
    first = SVC["standard"]
    initial = price("standard", 3, 2, "biweekly" if preset == "recurring" else "once") if preset in ("standard", "recurring") else price(preset, 3, 2)
    return f'''<form class="quote" data-ui data-quote novalidate aria-label="Price and booking">
<div class="quote-head"><h2>{E(heading)}</h2><p class="quote-total" aria-live="polite"><span data-total>${initial}</span><small data-per>per clean</small></p></div>
<div class="fields">
<div class="field field-wide"><label for="q-service">Type of clean</label><select id="q-service" name="service">{sel}</select></div>
<div class="field"><label for="q-beds">Bedrooms</label><select id="q-beds" name="beds">{beds}</select></div>
<div class="field"><label for="q-baths">Bathrooms</label><select id="q-baths" name="baths">{baths}</select></div>
<div class="field field-wide" data-freq-field><fieldset><legend>How often</legend><div class="chips">{freqs}</div></fieldset></div>
<div class="field field-wide"><fieldset><legend>Add-ons</legend><div class="chips">{adds}</div></fieldset></div>
<div class="field field-wide"><label for="q-zip">Zip code</label><input id="q-zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="341…"><span class="error" data-zip-msg role="status"></span></div>
<div class="field field-wide"><fieldset><legend>Next openings</legend><div class="chips" data-slots></div><p class="slots-empty" data-slots-empty>Text us and we'll offer the next opening during business hours.</p></fieldset></div>
</div>
<div class="quote-actions"><button class="btn btn-ink" type="submit" data-request>Request this clean</button>
<p class="quote-note" data-quote-note>Pay after the clean. Free re-clean within 48 hours.</p></div>
</form>'''


def quote_config(ctx):
    return {"pricing": PRICING, "zips": ZIPS, "slots": OPEN_SLOTS, "sampleSlots": SAMPLE_SLOTS if ctx.preview else [],
            "phone": B["phone_e164"], "phoneDisplay": B["phone_display"], "email": B["email"], "bookingUrl": B["booking_url"]}


def config_script(ctx):
    return f'<script>window.SUNNYMOP={json.dumps(quote_config(ctx))};</script>'


def points_section(ctx, heading="Every clean, room by room"):
    pts = [("Kitchen", "Counters, backsplash, sink and stovetop wiped and degreased."),
           ("Appliances", "Fronts of the fridge, oven and dishwasher; inside the microwave."),
           ("Bathrooms", "Showers, tubs, toilets, mirrors and glass scrubbed and disinfected."),
           ("Floors", "Vacuumed and mopped, edges and corners included."),
           ("Dusting", "Every reachable surface, ceiling fans, sills and switches."),
           ("Beds", "Made with fresh linens when you leave them out."),
           ("Lanai", "Furniture wiped and the floor swept."),
           ("Trash", "Emptied everywhere, with fresh liners."),
           ("Finish photos", "A few photos by text when we're done, if you're away.")]
    lis = "".join(f'<li><strong><span class="dot" aria-hidden="true"></span>{E(t)}</strong><p>{E(d)}</p></li>' for t, d in pts)
    return f'''<section class="section points-section" id="included"><div class="wrap">
{ctx.img("pier_sea_grapes", "circle-photo points-photo")}
<div><h2>{E(heading)}</h2><ul class="points">{lis}</ul></div>
</div></section>'''


def pricing_tiles(ctx):
    t = [("standard", "tile-1", "Standard", ["Kitchen, bathrooms and floors", "Dusting and beds", "Save up to 20% on a schedule"]),
         ("deep", "tile-2", "Deep", ["Everything in standard", "Baseboards and door frames", "Cabinet fronts and grout", "Hard-water spots on glass"]),
         ("moveout", "tile-3", "Move-in / move-out", ["Empty-home clean", "Inside cabinets and closets", "Inside fridge and oven", "Timed to your closing or lease", "Finish photos for the landlord"])]
    tiles = "".join(f'''<article class="tile {cls}"><div class="tile-body"><h3>{name}</h3><p class="price">${price(k, 1, 1)}<small> and up</small></p>
<ul>{"".join(f"<li>{E(x)}</li>" for x in lines)}</ul></div><a class="tile-strip" href="{ctx.href("book")}">Get my exact price <span aria-hidden="true">→</span></a></article>''' for k, cls, name, lines in t)
    return f'''<section class="section" id="pricing"><div class="wrap">
<div class="steps-grid"><div class="steps-head"><h2>Prices, upfront</h2><p class="lead">No phone call needed to find out what it costs.</p></div>{tiles}</div>
<p class="under-tiles">Starting prices are for a 1-bedroom, 1-bathroom home. A 3-bedroom, 2-bathroom standard clean is ${price("standard", 3, 2)}, or ${price("standard", 3, 2, "biweekly")} every two weeks. Airbnb turnovers start at ${PRICING["minimum"]}. <a href="{ctx.href("pricing")}">See every price</a>.</p>
</div></section>'''


def flow_svgs():
    # Many into one: scattered suns → a tight ribbon → neat rows. Drawn once, deterministic.
    import random
    rnd = random.Random(7)
    h_dots, v_dots = [], []
    for i in range(54):
        x, y = 20 + rnd.random() * 380, 20 + rnd.random() * 220
        h_dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 + rnd.random() * 3:.1f}" fill="{"#5c5a52" if i % 3 else "#8a8577"}"/>')
        v_dots.append(f'<circle cx="{20 + rnd.random() * 200:.1f}" cy="{20 + rnd.random() * 260:.1f}" r="{4 + rnd.random() * 3:.1f}" fill="{"#5c5a52" if i % 3 else "#8a8577"}"/>')
    for i in range(36):
        cx, cy = 450 + (i % 18) * 16, 112 + (i // 18) * 16 + 8
        h_dots.append(f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="#d9b23a"/>')
        v_dots.append(f'<circle cx="{104 + (i // 18) * 16}" cy="{330 + (i % 18) * 16}" r="6" fill="#d9b23a"/>')
    for i in range(48):
        cx, cy = 790 + (i % 12) * 30, 40 + (i // 12) * 56
        h_dots.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#ffc61a"/>')
        v_dots.append(f'<circle cx="{24 + (i % 6) * 36}" cy="{680 + (i // 6) * 40}" r="11" fill="#ffc61a"/>')
    h = f'<svg class="flow flow-h" viewBox="0 0 1160 260" role="img" aria-label="Scattered dots pulled into one tight line, then laid out in neat rows">{"".join(h_dots)}</svg>'
    v = f'<svg class="flow flow-v" viewBox="0 0 240 1000" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Scattered dots pulled into one tight line, then laid out in neat rows">{"".join(v_dots)}</svg>'
    return h, v


def how_band(ctx):
    h, v = flow_svgs()
    return f'''<section class="night" id="how"><div class="wrap">
<div class="night-head"><h2>Booked in a minute</h2><p class="lead">From a messy week to a clean home, with nothing to chase.</p></div>
{h}
<div class="flow-wrap">{v}
<ol class="flow-steps">
<li><h3>Book</h3><p>See your price and pick an opening online in about 60 seconds.</p></li>
<li><h3>We clean</h3><p>Your cleaner works through a room-by-room checklist for your home.</p></li>
<li><h3>You relax</h3><p>Pay after the clean. If anything's missed, we come back free within 48 hours.</p></li>
</ol></div>
</div></section>'''


def areas_section(ctx):
    frames = [("pier_sea_grapes", True), ("pier_walkers", False), ("pier_plaque", False)]
    imgs = "".join(ctx.img(k, "on" if on else "", extra=f' data-caption="{E(PHOTOS[k]["caption"])}"') for k, on in frames)
    links = "".join(f'<li><a href="{ctx.href("loc:" + l["slug"])}"><span class="dot" aria-hidden="true"></span>{E(l["name"])}</a></li>' for l in LOCATIONS)
    zips = "".join(f"<li>{z}</li>" for z in ZIPS)
    return f'''<section class="section areas-section" id="areas"><div class="wrap">
<div class="frame"><button class="frame-stage" type="button" data-frame aria-label="Show the next Naples photo">{imgs}</button>
<p class="frame-caption" data-frame-caption aria-live="polite">{E(PHOTOS["pier_sea_grapes"]["caption"])}</p></div>
<div class="area-copy"><h2>Where we clean</h2><p class="lead">Every Naples neighborhood, from the pier to Collier Boulevard.</p>
<ul class="area-list">{links}</ul>
<h3>Naples zip codes</h3><ul class="zips">{zips}</ul></div>
</div></section>'''


def before_after(ctx, service=None):
    items = [x for x in BEFORE_AFTER if service is None or x.get("service") == service]
    if not items:
        return ""
    cards = "".join(f'''<figure class="ba" style="--split:50%"><img src="{ctx.asset("img/" + x["before"])}" alt="{E(x["alt"])}, before" loading="lazy">
<img class="after" src="{ctx.asset("img/" + x["after"])}" alt="{E(x["alt"])}, after" loading="lazy">
<input type="range" min="0" max="100" value="50" aria-label="Slide to compare before and after" oninput="this.parentNode.style.setProperty('--split', this.value + '%')"></figure>''' for x in items)
    return f'<section class="section"><div class="wrap"><h2>Before and after</h2><p class="lead">Real SunnyMop jobs in Naples.</p><div class="ba-grid">{cards}</div></div></section>'


def faq_block(items, heading="Questions, answered", aside=""):
    tiles = "".join(f'<details name="faq"><summary>{E(q)}<span class="pm" aria-hidden="true"></span></summary><p>{E(a)}</p></details>' for q, a in items)
    return f'''<section class="section faq-section" id="faq"><div class="wrap">
<div class="faq-head"><h2>{E(heading)}</h2>{aside}</div><div class="faq">{tiles}</div>
</div></section>'''


def coupon(ctx):
    svc = "".join(f'<option value="{s["name"]}">{E(s["name"])}</option>' for s in SERVICES)
    return f'''<section class="section" id="offer"><div class="wrap">
<div class="coupon">
<div class="coupon-left">{ctx.img("surf", "coupon-photo")}<div class="stack"><h2>${B["first_clean_off"]} off your first clean</h2>
<p>Send this and we'll text you back with your price and the next opening.</p></div></div>
<form class="coupon-form" data-offer novalidate aria-label="Claim your first-clean offer">
<label class="visually-hidden" for="o-name">Name</label><input id="o-name" name="name" autocomplete="name" placeholder="Your name" required>
<label class="visually-hidden" for="o-phone">Mobile number</label><input id="o-phone" name="phone" type="tel" autocomplete="tel" placeholder="Mobile number" required>
<label class="visually-hidden" for="o-zip">Zip code</label><input id="o-zip" name="zip" inputmode="numeric" maxlength="5" autocomplete="postal-code" placeholder="Zip code">
<label class="visually-hidden" for="o-service">Service</label><select id="o-service" name="service">{svc}</select>
<button class="btn btn-ink" type="submit">Claim ${B["first_clean_off"]} off</button><p class="form-msg" data-offer-msg role="status"></p>
</form></div></div></section>'''


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def home(ctx, wrapper=True):
    title = "House Cleaning Naples, FL | SunnyMop"
    if PROOF["review_count"] and PROOF["rating"]:
        title += f' | {PROOF["review_count"]}+ Five-Star Reviews'
    desc = (f"Premium house cleaning in Naples, FL: standard, deep, move-out and Airbnb cleaning from ${price('standard', 1, 1)}. "
            f"${B['first_clean_off']} off your first clean. Call or text {B['phone_display']}.")
    svc_links = "".join(f'<li><a href="{ctx.href("svc:" + s["key"])}"><h3>{E(s["name"])}</h3><span class="from">from ${price(s["kind"], 1, 1, "biweekly" if s["key"] == "recurring" else "once")}</span><p>{E(s["short"])}</p></a></li>' for s in SERVICES)
    body = f'''<section class="hero"><div class="hero-sun" aria-hidden="true"></div><div class="wrap">
<div class="hero-copy"><h1>House cleaning in Naples, FL</h1>
<p class="lead">Premium standard, deep, move-out and Airbnb cleaning. See your exact price now and pick the next opening.</p>
<div class="hero-actions"><a class="btn btn-ink" href="#quote">See my price</a><a class="btn btn-plain" href="sms:{B["phone_e164"]}">Text {E(B["phone_display"])}</a></div>
{promises()}</div>
<div class="hero-quote" id="quote">{quote_widget(ctx)}</div>
</div></section>
{points_section(ctx)}
{pricing_tiles(ctx)}
{how_band(ctx)}
<section class="section" id="services"><div class="wrap"><div class="services-head"><h2>Our services</h2><p class="lead">Five ways to get a clean Naples home.</p></div>
<ul class="svc-list">{svc_links}</ul></div></section>
{before_after(ctx)}
{areas_section(ctx)}
{faq_block(FAQ[:8], aside=f'<p><a href="{ctx.href("faq")}">All questions</a></p>')}
{coupon(ctx)}'''
    return page(ctx, "index", title, desc, config_script(ctx) + body, schema=[business_schema(), faq_schema(FAQ[:8])],
                wrapper=wrapper, scripts=("site.js",))


def service_page(ctx, s):
    trail = [("index", "Home"), ("svc:" + s["key"], s["name"])]
    inc = "".join(f'<li><span class="dot" aria-hidden="true"></span><span>{E(x)}</span></li>' for x in s["included"])
    related = "".join(f'<li><a href="{ctx.href("svc:" + o["key"])}">{E(o["name"])}</a></li>' for o in SERVICES if o is not s)
    near = "".join(f'<li><a href="{ctx.href("loc:" + l["slug"])}">{E(s["name"])} in {E(l["name"])}</a></li>' for l in LOCATIONS)
    kind = s["kind"]
    start = price(kind, 1, 1, "biweekly" if s["key"] == "recurring" else "once")
    preset = "recurring" if s["key"] == "recurring" else kind
    photo = {"standard": "palms", "deep": "pier_walkers", "moveout": "wide_beach", "airbnb": "surf", "recurring": "pier_sea_grapes"}[s["key"]]
    schema = {"@context": "https://schema.org", "@type": "Service", "name": s["h1"], "serviceType": s["name"],
              "provider": {"@id": B["domain"] + "/#business"}, "areaServed": {"@type": "City", "name": "Naples, FL"},
              "offers": {"@type": "Offer", "priceCurrency": "USD", "price": str(start), "description": "Starting price, 1-bedroom 1-bathroom home"},
              "url": ctx.canonical("svc:" + s["key"])}
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">{E(s["name"])}</li></ol></nav>
<section class="page-hero"><div class="wrap"><div class="copy"><h1>{E(s["h1"])}</h1><p class="lead">{E(s["lead"])}</p>
<div class="hero-actions"><a class="btn btn-sun" href="#quote">From ${start}: see my price</a><a class="btn btn-plain" href="sms:{B["phone_e164"]}">Text us</a></div>{promises()}</div>
{ctx.img(photo, "circle-photo", lazy=False)}</div></section>
<section class="section"><div class="wrap two-col">
<div class="prose"><h2>What's included</h2><ul class="checklist">{inc}</ul>
<h2>Who it's for</h2><p>{E(s["good_for"])}</p>
<h2>Related services</h2><ul class="links-band">{related}</ul>
<h2>{E(s["name"])} across Naples</h2><ul class="links-band">{near}</ul></div>
<div class="sticky-quote" id="quote">{quote_widget(ctx, preset=preset, heading="Your price")}</div>
</div></section>
{before_after(ctx, s["slug"])}
{faq_block(s["faq"], heading="Questions about " + s["name"].lower())}'''
    return page(ctx, "svc:" + s["key"], f'{s["h1"]} | SunnyMop', f'{s["lead"][:120].rsplit(" ", 1)[0]}. From ${start}. Instant price online.',
                config_script(ctx) + body, active="svc:standard", schema=[schema, crumbs_schema(ctx, trail), faq_schema(s["faq"])], scripts=("site.js",))


def location_page(ctx, l):
    trail = [("index", "Home"), ("loc:" + l["slug"], l["name"])]
    paras = "".join(f"<p>{E(p)}</p>" for p in l["body"])
    links = "".join(f'<li><a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a></li>' for s in SERVICES)
    others = "".join(f'<li><a href="{ctx.href("loc:" + o["slug"])}">{E(o["name"])}</a></li>' for o in LOCATIONS if o is not l)
    zips = "".join(f"<li>{z}</li>" for z in l["zips"])
    schema = business_schema() | {"areaServed": {"@type": "Place", "name": f'{l["name"]}, Naples, FL'}}
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">{E(l["name"])}</li></ol></nav>
<section class="page-hero"><div class="wrap"><div class="copy"><h1>House cleaning in {E(l["name"])}</h1><p class="lead">{E(l["lead"])}</p>
<div class="hero-actions"><a class="btn btn-sun" href="#quote">See my price</a><a class="btn btn-plain" href="sms:{B["phone_e164"]}">Text us</a></div></div>
{ctx.img("pier_walkers" if l["slug"] == "old-naples" else ("wide_beach" if "beach" in l["slug"] or l["slug"] == "park-shore" else "palms"), "circle-photo", lazy=False)}</div></section>
<section class="section"><div class="wrap two-col">
<div class="prose"><h2>Cleaning in {E(l["name"])}</h2>{paras}
<h2>Zip codes</h2><ul class="zips">{zips}</ul>
<h2>Services in {E(l["name"])}</h2><ul class="links-band">{links}</ul>
<h2>Nearby</h2><ul class="links-band">{others}</ul></div>
<div class="sticky-quote" id="quote">{quote_widget(ctx)}</div>
</div></section>'''
    return page(ctx, "loc:" + l["slug"], f'House Cleaning {l["name"]}, Naples FL | SunnyMop', l["lead"][:155],
                config_script(ctx) + body, active="index#areas", schema=[schema, crumbs_schema(ctx, trail)], scripts=("site.js",))


def pricing_page(ctx):
    trail = [("index", "Home"), ("pricing", "Pricing")]
    sizes = [(1, 1), (2, 2), (3, 2), (4, 3), (5, 4)]
    head = "".join(f"<th>{b} bed · {ba} bath</th>" for b, ba in sizes)
    rows = [("Standard, one time", "standard", "once"), ("Standard, weekly", "standard", "weekly"), ("Standard, every 2 weeks", "standard", "biweekly"),
            ("Standard, monthly", "standard", "monthly"), ("Deep", "deep", "once"), ("Move-in / move-out", "moveout", "once"), ("Airbnb turnover", "airbnb", "once")]
    trs = "".join(f"<tr><th scope=\"row\">{E(n)}</th>" + "".join(f'<td class="n">${price(k, b, ba, f)}</td>' for b, ba in sizes) + "</tr>" for n, k, f in rows)
    adds = "".join(f'<tr><th scope="row">{E(n)}</th><td class="n">${p}</td></tr>' for _, n, p in PRICING["addons"])
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">Pricing</li></ol></nav>
<section class="page-hero"><div class="wrap"><div class="copy"><h1>House cleaning prices in Naples</h1>
<p class="lead">Every price, by home size. Pay after the clean.</p></div>{ctx.img("pier_plaque", "circle-photo", lazy=False)}</div></section>
<section class="section"><div class="wrap prose" style="max-width:none">
<div class="table-scroll"><table><thead><tr><th>Service</th>{head}</tr></thead><tbody>{trs}</tbody></table></div>
<h2>Add-ons</h2><div class="table-scroll" style="max-width:560px"><table><tbody>{adds}</tbody></table></div>
<h2>Good to know</h2><ul class="checklist">
<li><span class="dot"></span><span>Minimum ${PRICING["minimum"]} for any visit.</span></li>
<li><span class="dot"></span><span>Recurring plans start with a deep clean, so every visit after holds that level.</span></li>
<li><span class="dot"></span><span>Homes over 5 bedrooms or 4,000 square feet get a custom quote.</span></li>
<li><span class="dot"></span><span>Not included: exterior windows, biohazards, mold or pest cleanup, and moving heavy furniture.</span></li>
<li><span class="dot"></span><span>Move or cancel free with 48 hours' notice.</span></li></ul>
<p><a class="btn btn-sun" href="{ctx.href("book")}">Get my exact price</a></p>
</div></section>'''
    return page(ctx, "pricing", "House Cleaning Prices Naples, FL | SunnyMop",
                f"SunnyMop prices by home size: standard from ${price('standard', 1, 1)}, deep from ${price('deep', 1, 1)}, move-out from ${price('moveout', 1, 1)}. Recurring plans save up to 20%.",
                body, active="pricing", schema=[crumbs_schema(ctx, trail)])


def faq_page(ctx):
    trail = [("index", "Home"), ("faq", "FAQ")]
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">FAQ</li></ol></nav>
{faq_block(FAQ, heading="House cleaning questions")}
{coupon(ctx)}'''
    return page(ctx, "faq", "House Cleaning FAQ | SunnyMop Naples, FL",
                "Answers about SunnyMop house cleaning in Naples: prices, access while you're away, supplies, guarantee, payment and cancellations.",
                config_script(ctx) + body, active="faq", schema=[faq_schema(FAQ), crumbs_schema(ctx, trail)], scripts=("site.js",))


def about_page(ctx):
    trail = [("index", "Home"), ("about", "About")]
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">About</li></ol></nav>
<section class="page-hero"><div class="wrap"><div class="copy"><h1>A cleaner way to book</h1>
<p class="lead">SunnyMop is a new Naples house cleaning company built to be easy to trust.</p></div>{ctx.img("palms", "circle-photo", lazy=False)}</div></section>
<section class="section"><div class="wrap prose">
<p>Hiring a cleaner shouldn't feel like a gamble. So we show every price upfront, we charge only after the clean, and if something's missed we come back free within 48 hours.</p>
<p>Every visit follows a written, room-by-room checklist, so the clean you get on your tenth visit matches the first. You can ask for the same cleaner every time, and if you're away, we text finish photos.</p>
<p>We clean homes, condos and vacation rentals across Naples, from Old Naples to East Naples.</p>
<p><a class="btn btn-sun" href="{ctx.href("book")}">Get my price</a></p>
</div></section>'''
    return page(ctx, "about", "About SunnyMop | House Cleaning in Naples, FL",
                "SunnyMop is a Naples house cleaning company: prices upfront, pay after the clean, and a free re-clean within 48 hours.",
                body, active=None, schema=[crumbs_schema(ctx, trail)])


def book_page(ctx):
    trail = [("index", "Home"), ("book", "Book")]
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">Book</li></ol></nav>
<section class="section" style="padding-top:48px"><div class="wrap two-col">
<div class="prose"><h1 style="font-size:clamp(2.6rem,1.4rem + 4.6vw,5.6rem)">Get your price</h1>
<p class="lead">Pick the clean, your home size and an opening. We confirm by text.</p>
<ul class="checklist"><li><span class="dot"></span><span>Pay after the clean, never before</span></li>
<li><span class="dot"></span><span>Free re-clean within 48 hours</span></li><li><span class="dot"></span><span>Move or cancel free with 48 hours' notice</span></li></ul>
<p>Prefer to talk? Call or text <strong class="num">{E(B["phone_display"])}</strong>, {E(B["hours"])}.</p></div>
<div id="quote">{quote_widget(ctx)}</div></div></section>'''
    return page(ctx, "book", "Book House Cleaning in Naples, FL | SunnyMop",
                "See your exact house cleaning price for your Naples home and request the next opening in about a minute.",
                config_script(ctx) + body, active=None, schema=[crumbs_schema(ctx, trail)], scripts=("site.js",))


def contact_page(ctx):
    trail = [("index", "Home"), ("contact", "Contact")]
    body = f'''<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">Contact</li></ol></nav>
<section class="page-hero"><div class="wrap"><div class="copy"><h1>Talk to SunnyMop</h1>
<p class="lead">Call or text <span class="num">{E(B["phone_display"])}</span>. Email {E(B["email"])}. {E(B["hours"])}.</p>
<div class="hero-actions"><a class="btn btn-sun" href="sms:{B["phone_e164"]}">Text us</a><a class="btn btn-plain" href="tel:{B["phone_e164"]}">Call us</a></div></div>
{ctx.img("wide_beach", "circle-photo", lazy=False)}</div></section>
{coupon(ctx)}'''
    return page(ctx, "contact", "Contact SunnyMop | House Cleaning Naples, FL",
                f"Call or text SunnyMop at {B['phone_display']} for house cleaning in Naples, FL. {B['hours']}.",
                config_script(ctx) + body, active="contact", schema=[business_schema(), crumbs_schema(ctx, trail)], scripts=("site.js",))


def not_found(ctx):
    body = f'''<section class="section"><div class="wrap prose"><h1 style="font-size:var(--step-head)">Page not found</h1>
<p class="lead">That page doesn't exist.</p><p><a class="btn btn-sun" href="{ctx.href("book")}">Get my price</a></p></div></section>'''
    return page(ctx, "404", "Page not found | SunnyMop", "Page not found.", body, noindex=True)


# ---------------------------------------------------------------------------
# Brand kit and checklist
# ---------------------------------------------------------------------------
BRAND = {
    "idea": "The sun in the name is the brand's only shape. It's the 'o' in the wordmark, every button, every photo frame and every list mark.",
    "positioning": "SunnyMop is premium house cleaning in Naples that's easy to trust: every price upfront, payment after the clean, and a free re-clean within 48 hours.",
    "words_yes": ["Judgement-free", "Guaranteed", "Trustworthy", "Ready when you are"],
    "words_no": ["Cheap", "Scammy", "Low quality", "Untrustworthy"],
    "taglines": ["Your satisfaction is the job.", "A cleaner home, guaranteed.", "Sunny side up, every room."],
    "colors": [("Sun", "#FFC61A", "Logo 'o', main buttons, the hero sun, open FAQ"), ("Ink", "#0B0B0B", "Text, dark band, secondary buttons"),
               ("Paper", "#F7F7F5", "Page background"), ("Stone", "#EBEBE8", "Form fields, quiet surfaces, footer"),
               ("Palm", "#BDF29D", "Pricing tile"), ("Gulf", "#93ECE9", "Pricing tile"), ("Sky", "#A9B8F7", "Pricing tile")],
    "type": "Schibsted Grotesk (Google Fonts): 800 for headlines with tight tracking (-0.05em), 400 for text, 600 for labels and buttons.",
}


def brand_kit_page(ctx):
    sw = "".join(f'<li style="display:grid;gap:8px"><span style="display:block;width:112px;aspect-ratio:1;border-radius:50%;background:{c}"></span><strong>{E(n)}</strong><span class="num">{c}</span><span class="small">{E(u)}</span></li>' for n, c, u in BRAND["colors"])
    body = f'''<section class="section" style="padding-top:56px"><div class="wrap prose" style="max-width:none">
<h1 style="font-size:var(--step-head)">SunnyMop brand kit</h1><p class="lead">{E(BRAND["positioning"])}</p>
<p class="big-mark" aria-label="SunnyMop wordmark" style="font-size:clamp(4rem,2rem + 10vw,11rem)">sunnym<span class="sun-o"></span>p</p>
<p>{E(BRAND["idea"])}</p>
<h2>Colors</h2><ul style="list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:28px">{sw}</ul>
<h2>Type</h2><p>{E(BRAND["type"])}</p>
<h2>Taglines</h2><ul class="checklist">{"".join(f'<li><span class="dot"></span><span>{E(t)}</span></li>' for t in BRAND["taglines"])}</ul>
<h2>Feel</h2><p>Always: {E(", ".join(BRAND["words_yes"]))}. Never: {E(", ".join(BRAND["words_no"]))}.</p>
<h2>Photos to shoot (your own jobs)</h2><ul class="checklist">
<li><span class="dot"></span><span>Stovetops and ovens before and after: the highest-impact shot</span></li>
<li><span class="dot"></span><span>Baseboards, grout and shower glass close-ups</span></li>
<li><span class="dot"></span><span>Bathroom vanities and fridges, same angle and light before and after</span></li>
<li><span class="dot"></span><span>Landscape orientation, nothing that identifies the client's home</span></li></ul>
</div></section>'''
    return page(ctx, "brand-kit", "SunnyMop Brand Kit", "Logo, colors, type and voice for SunnyMop.", body, noindex=True)


CHECKLIST = [
    ("Before launch", ["Check 'SunnyMop' on Sunbiz and the USPTO trademark search; register the name or a fictitious name",
                       "Buy the domain and set it in site/build.py",
                       "Set your real phone, email and first-clean offer in site/build.py",
                       "Bind insurance, then set insured: True. Do the same for bonded and background checks",
                       "Add real openings to OPEN_SLOTS, or a booking link to booking_url",
                       "Deploy site/public to Cloudflare Pages and connect the domain"]),
    ("Photos", ["Shoot your first 5 before-and-after pairs (ovens and stovetops first)",
                "Save them as WebP with names like deep-cleaning-oven-before-naples.webp and list them in BEFORE_AFTER",
                "Replace the beach stock photos with your own Naples shots over time"]),
    ("Google", ["Create and verify your Google Business Profile as a service-area business in Naples",
                "Submit sitemap.xml in Google Search Console",
                "Add your GA4 id to ga4_id in site/build.py",
                "Ask every client for a review; set review_count and rating once you have them"]),
    ("Listings (same name and phone everywhere)", ["Yelp", "Nextdoor", "Facebook", "Angi", "Thumbtack", "BBB", "Apple Business Connect", "Bing Places"]),
    ("Content", ["Blog: How much does house cleaning cost in Naples? (2026 guide)", "Blog: Move-out cleaning checklist for Florida rentals",
                 "Blog: Deep cleaning vs. regular cleaning", "Blog: Hurricane-season cleanup and prep"]),
]


def checklist_page(ctx):
    n = 0
    secs = []
    for t, items in CHECKLIST:
        lis = []
        for it in items:
            n += 1
            lis.append(f'<li><span class="dot"></span><label for="c{n}"><input type="checkbox" id="c{n}"> {E(it)}</label></li>')
        secs.append(f'<h2>{E(t)}</h2><ul class="checklist">{"".join(lis)}</ul>')
    body = f'''<section class="section" style="padding-top:56px"><div class="wrap prose"><h1 style="font-size:var(--step-head)">SunnyMop launch checklist</h1>{"".join(secs)}</div></section>'''
    return page(ctx, "checklist", "SunnyMop Launch Checklist", "Launch checklist for SunnyMop.", body, noindex=True)


def brand_md():
    out = ["# SunnyMop brand kit", "", "Generated by `site/build.py`.", "", BRAND["positioning"], "", "## Idea", "", BRAND["idea"], "",
           "## Wordmark", "", "Lowercase `sunnymop` in Schibsted Grotesk 800, tracking -0.06em, with the `o` replaced by a filled Sun circle. "
           "`brand/wordmark.svg` uses live text; outline it in Figma or Canva before sending to a printer.", "", "## Colors", "", "| Name | Hex | Use |", "| --- | --- | --- |"]
    out += [f"| {n} | `{c}` | {u} |" for n, c, u in BRAND["colors"]]
    out += ["", "## Type", "", BRAND["type"], "", "## Taglines", ""] + [f"- {t}" for t in BRAND["taglines"]]
    out += ["", "## Feel", "", "Always: " + ", ".join(BRAND["words_yes"]) + ". Never: " + ", ".join(BRAND["words_no"]) + ".", ""]
    return "\n".join(out)


def checklist_md():
    out = ["# SunnyMop launch checklist", "", "Generated by `site/build.py`.", ""]
    for t, items in CHECKLIST:
        out += [f"## {t}", ""] + [f"- [ ] {i}" for i in items] + [""]
    return "\n".join(out)


WORDMARK_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 120" width="520" height="120">
<text x="0" y="92" font-family="'Schibsted Grotesk', Arial, sans-serif" font-weight="800" font-size="112" letter-spacing="-6.7" fill="#0b0b0b">sunnym</text>
<circle cx="412" cy="70" r="31" fill="#ffc61a"/>
<text x="446" y="92" font-family="'Schibsted Grotesk', Arial, sans-serif" font-weight="800" font-size="112" letter-spacing="-6.7" fill="#0b0b0b">p</text>
</svg>
'''
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#ffc61a"/></svg>\n'


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def all_pages(ctx):
    pages = {"index": home(ctx), "pricing": pricing_page(ctx), "faq": faq_page(ctx), "about": about_page(ctx),
             "book": book_page(ctx), "contact": contact_page(ctx), "404": not_found(ctx)}
    for s in SERVICES:
        pages["svc:" + s["key"]] = service_page(ctx, s)
    for l in LOCATIONS:
        pages["loc:" + l["slug"]] = location_page(ctx, l)
    return pages


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def copy_static(dest):
    shutil.copy(ROOT / "static" / "styles.css", dest / "styles.css")
    shutil.copy(ROOT / "static" / "site.js", dest / "site.js")
    shutil.copytree(ROOT / "static" / "img", dest / "img", dirs_exist_ok=True)
    write(dest / "favicon.svg", FAVICON)


def build():
    out = ROOT / "public"
    shutil.rmtree(out, ignore_errors=True)
    ctx = Ctx(False)
    pages = all_pages(ctx)
    for k, t in pages.items():
        write(out / live_file(k), t)
    urls = "".join(f"<url><loc>{ctx.canonical(k)}</loc></url>" for k in pages if k != "404")
    write(out / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write(out / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {B['domain']}/sitemap.xml\n")
    copy_static(out)

    prev = ROOT / "preview"
    shutil.rmtree(prev, ignore_errors=True)
    pctx = Ctx(True)
    pp = all_pages(pctx)
    pp["brand-kit"] = brand_kit_page(pctx)
    pp["checklist"] = checklist_page(pctx)
    for k, t in pp.items():
        write(prev / preview_file(k), t)
    entry = home(pctx, wrapper=False).replace("<title>House Cleaning Naples, FL | SunnyMop</title>", "<title>SunnyMop Website</title>", 1)
    write(prev / "index.html", entry)
    copy_static(prev)

    write(REPO / "brand" / "BRAND.md", brand_md())
    write(REPO / "brand" / "wordmark.svg", WORDMARK_SVG)
    write(REPO / "brand" / "sun-mark.svg", FAVICON)
    write(REPO / "docs" / "launch-checklist.md", checklist_md())
    print(f"Built {len(pages)} live pages, {len(pp) + 1} preview pages.")


if __name__ == "__main__":
    build()
