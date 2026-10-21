#!/usr/bin/env python3
"""Build the Sea Grape Home Cleaning website, brand kit and launch checklist.

Usage:  python3 site/build.py

Writes:
  site/public/   the live website (deploy this folder to Cloudflare Pages)
  site/preview/  a preview copy with relative links and a placeholder banner
  brand/BRAND.md and docs/seo-and-channels-checklist.md

Edit BUSINESS below before going live. Everything marked PLACEHOLDER must be replaced.
"""
import html
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

# ---------------------------------------------------------------------------
# Business details (PLACEHOLDER values must be replaced before launch)
# ---------------------------------------------------------------------------
BUSINESS = {
    "name": "Sea Grape Home Cleaning",
    "short": "Sea Grape",
    "domain": "https://www.seagrapecleaning.com",  # PLACEHOLDER: check availability and buy
    "phone_display": "(239) 555-0100",  # PLACEHOLDER: your Quo number with a 239 area code
    "phone_e164": "+12395550100",
    "email": "hello@seagrapecleaning.com",  # PLACEHOLDER
    "booking_url": "https://example.com/book",  # PLACEHOLDER: your ZenMaid or Jobber booking page
    "hours": "Mon–Sat, 8 AM–6 PM",
    "hours_schema": ["Mo-Sa 08:00-18:00"],
    "year": 2026,
    "same_as": [],  # add Google Business Profile, Facebook, Instagram URLs once live
}

AREAS = {
    "naples": {
        "name": "Naples",
        "zips": ["34102", "34103", "34104", "34105", "34108", "34109", "34110",
                 "34112", "34113", "34114", "34116", "34117", "34119", "34120"],
        "places": ["Old Naples", "Park Shore", "Pelican Bay", "Vanderbilt Beach",
                   "Naples Park", "Golden Gate", "Lely", "East Naples"],
    },
    "marco-island": {"name": "Marco Island", "zips": ["34145"], "places": []},
    "bonita-springs": {"name": "Bonita Springs", "zips": ["34134", "34135"], "places": []},
    "estero": {"name": "Estero", "zips": ["33928"], "places": []},
}

# ---------------------------------------------------------------------------
# Pricing (shared by the pricing table, service pages and the estimator)
# ---------------------------------------------------------------------------
BASE_FIXED, PER_BED, PER_BATH = 85, 20, 20
MULT = {
    "weekly": 0.90, "biweekly": 1.00, "monthly": 1.12, "onetime": 1.25,
    "deep": 1.70, "moveout": 1.85, "seasonal": 1.40,
}
RENTAL_FIXED, RENTAL_PER_ROOM = 60, 15
ADDONS = [("fridge", "Inside the fridge", 35), ("oven", "Inside the oven", 35),
          ("windows", "Interior windows", 40), ("laundry", "Laundry, wash and fold", 30)]


def round5(x):
    return int(math.floor(x / 5 + 0.5) * 5)


def price(kind, bed, bath):
    if kind == "rental":
        return round5(RENTAL_FIXED + RENTAL_PER_ROOM * (bed + bath))
    return round5((BASE_FIXED + PER_BED * bed + PER_BATH * bath) * MULT[kind])


SIZES = [(2, 2), (3, 2), (4, 3), (5, 4)]

SERVICES = [
    {"slug": "recurring-cleaning", "kind": "biweekly", "name": "Recurring cleaning",
     "blurb": "Weekly, every two weeks or monthly. The same checklist every visit, and the same cleaner whenever we can."},
    {"slug": "deep-cleaning", "kind": "deep", "name": "Deep cleaning",
     "blurb": "Baseboards, door frames, cabinet fronts, grout and fixtures. Every recurring plan starts with one."},
    {"slug": "move-out-cleaning", "kind": "moveout", "name": "Move-in and move-out cleaning",
     "blurb": "Empty-home cleaning timed to your closing or lease end, with a photo report for the landlord or buyer."},
    {"slug": "seasonal-home-cleaning", "kind": "seasonal", "name": "Seasonal home cleaning",
     "blurb": "A closing clean when you leave for the summer and an opening clean before you're back."},
    {"slug": "vacation-rental-cleaning", "kind": "rental", "name": "Vacation rental turnovers",
     "blurb": "Same-day turnovers between guests, with damage and supply photos sent to the host."},
]


def from_price(svc):
    return price(svc["kind"], 2, 2)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
E = html.escape
B = BUSINESS


class Ctx:
    def __init__(self, preview):
        self.preview = preview

    def href(self, slug):
        if self.preview:
            return "home.html" if slug == "index" else f"{slug}.html"
        return "/" if slug == "index" else f"/{slug}"

    def canonical(self, slug):
        return B["domain"] + ("/" if slug == "index" else f"/{slug}")

    def asset(self, name):
        return name if self.preview else f"/{name}"


def logo_svg(size=40, label=True):
    aria = f'role="img" aria-label="{E(B["name"])} logo"' if label else 'aria-hidden="true"'
    return f'''<svg viewBox="0 0 64 64" width="{size}" height="{size}" {aria}>
<path d="M30 52C14 48 5 36 7 23 9 11 21 4 32 6c14 2 24 12 22 26-2 12-12 20-24 20z" fill="var(--leaf)"/>
<path d="M30 52V15M30 41l-11-8M30 41l12-8M30 30l-13-8M30 30l14-8M30 21l-8-5M30 21l9-5" stroke="var(--paper)" stroke-width="2.2" stroke-linecap="round" fill="none"/>
<circle cx="47" cy="51" r="5" fill="var(--grape)"/><circle cx="56" cy="47" r="5" fill="var(--grape)"/><circle cx="53" cy="57" r="5" fill="var(--grape)"/>
</svg>'''


LOGO_FILE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
<path d="M30 52C14 48 5 36 7 23 9 11 21 4 32 6c14 2 24 12 22 26-2 12-12 20-24 20z" fill="#2e6b57"/>
<path d="M30 52V15M30 41l-11-8M30 41l12-8M30 30l-13-8M30 30l14-8M30 21l-8-5M30 21l9-5" stroke="#f5f8f6" stroke-width="2.2" stroke-linecap="round" fill="none"/>
<circle cx="47" cy="51" r="5" fill="#6a3d6e"/><circle cx="56" cy="47" r="5" fill="#6a3d6e"/><circle cx="53" cy="57" r="5" fill="#6a3d6e"/>
</svg>
'''

LOGO_HORIZONTAL_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 72" width="360" height="72">
<g transform="translate(4 4)">
<path d="M30 52C14 48 5 36 7 23 9 11 21 4 32 6c14 2 24 12 22 26-2 12-12 20-24 20z" fill="#2e6b57"/>
<path d="M30 52V15M30 41l-11-8M30 41l12-8M30 30l-13-8M30 30l14-8M30 21l-8-5M30 21l9-5" stroke="#f5f8f6" stroke-width="2.2" stroke-linecap="round" fill="none"/>
<circle cx="47" cy="51" r="5" fill="#6a3d6e"/><circle cx="56" cy="47" r="5" fill="#6a3d6e"/><circle cx="53" cy="57" r="5" fill="#6a3d6e"/>
</g>
<text x="80" y="38" font-family="'Bricolage Grotesque', 'Avenir Next', sans-serif" font-weight="700" font-size="32" fill="#13241f">Sea Grape</text>
<text x="81" y="60" font-family="'IBM Plex Mono', monospace" font-size="12.5" letter-spacing="2.4" fill="#4f625c">HOME CLEANING</text>
</svg>
'''

FONTS = ("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700"
         "&family=Bricolage+Grotesque:opsz,wght@12..96,600..800"
         "&family=IBM+Plex+Mono:wght@400;500&display=swap")

NAV = [("services", "Services"), ("areas", "Areas"), ("pricing", "Pricing"), ("faq", "FAQ"), ("about", "About")]


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def business_schema(ctx):
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": B["domain"] + "/#business",
        "name": B["name"],
        "url": B["domain"] + "/",
        "logo": B["domain"] + "/logo.svg",
        "image": B["domain"] + "/logo.svg",
        "telephone": B["phone_e164"],
        "email": B["email"],
        "priceRange": "$$",
        "description": "House cleaning for homes, condos and vacation rentals in Naples, Marco Island, Bonita Springs and Estero, Florida.",
        "areaServed": [{"@type": "City", "name": f"{a['name']}, FL"} for a in AREAS.values()],
        "openingHours": B["hours_schema"],
        "sameAs": B["same_as"],
    }


def breadcrumb_schema(ctx, trail):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": ctx.canonical(slug)}
            for i, (slug, name) in enumerate(trail)
        ],
    }


def crumbs_html(ctx, trail):
    items = []
    for i, (slug, name) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li aria-current="page">{E(name)}</li>')
        else:
            items.append(f'<li><a href="{ctx.href(slug)}">{E(name)}</a></li>')
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def nav_target(ctx, key):
    return {"services": ctx.href("index") + ("#services" if not ctx.preview else "#services"),
            "areas": ctx.href("index") + "#areas"}.get(key, ctx.href(key))


def header(ctx, active):
    current = ' aria-current="page"'
    links = "".join(
        f'<a href="{nav_target(ctx, k)}"{current if k == active else ""}>{E(label)}</a>'
        for k, label in NAV)
    menu_links = "".join(f'<a href="{nav_target(ctx, k)}">{E(label)}</a>' for k, label in NAV)
    preview_bar = ""
    if ctx.preview:
        preview_bar = f'''<div class="preview-bar"><div class="wrap"><strong>PREVIEW</strong>
<span>Phone, email, domain and booking link are placeholders.</span>
<a href="brand-kit.html">Brand kit</a><a href="checklist.html">Launch checklist</a><a href="home.html">Website</a></div></div>'''
    return f'''<a class="skip" href="#main">Skip to content</a>
{preview_bar}
<header class="site-header"><div class="wrap">
<a class="brand" href="{ctx.href("index")}">{logo_svg(40, label=False)}<span class="brand-name">Sea Grape<small>Home Cleaning</small></span></a>
<nav class="nav" aria-label="Main">{links}</nav>
<span class="header-call mono">{E(B["phone_display"])}</span>
<a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a>
<details class="menu"><summary>Menu</summary><div class="menu-panel">{menu_links}<a href="{ctx.href("book")}">Get your price</a></div></details>
</div></header>'''


def footer(ctx):
    svc = "".join(f'<li><a href="{ctx.href(s["slug"])}">{E(s["name"])}</a></li>' for s in SERVICES)
    areas = "".join(
        f'<li><a href="{ctx.href("index" if k == "naples" else k)}">{E(a["name"])}, FL</a></li>'
        for k, a in AREAS.items())
    return f'''<footer class="site-footer"><div class="wrap">
<div><h2>{E(B["name"])}</h2><ul>
<li>Call or text <span class="mono">{E(B["phone_display"])}</span></li>
<li>{E(B["email"])}</li><li>{E(B["hours"])}</li></ul></div>
<div><h2>Services</h2><ul>{svc}</ul></div>
<div><h2>Areas</h2><ul>{areas}</ul></div>
<div><h2>Company</h2><ul><li><a href="{ctx.href("pricing")}">Pricing</a></li><li><a href="{ctx.href("faq")}">FAQ</a></li>
<li><a href="{ctx.href("about")}">About</a></li><li><a href="{ctx.href("book")}">Book a clean</a></li></ul></div>
<p class="fine">© {B["year"]} {E(B["name"])}. Serving Collier and southern Lee County, Florida.</p>
</div></footer>'''


def page(ctx, slug, title, description, body, active=None, schema=(), noindex=False, wrapper=True):
    canonical = ctx.canonical(slug)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    ld = "".join(jsonld(s) for s in schema)
    headbits = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(description)}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{E(B["name"])}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{ctx.asset("favicon.svg")}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{ctx.asset("styles.css")}">
{ld}'''
    content = f'''{header(ctx, active)}
<main id="main">
{body}
</main>
{footer(ctx)}'''
    if not wrapper:
        return headbits + "\n" + content + "\n"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{headbits}
</head>
<body>
{content}
</body>
</html>
'''


def cta_band(ctx, heading="See your price in a minute",
             text="Pick your home size and how often you want a clean. You'll see the price before you book."):
    return f'''<section class="band"><div class="wrap">
<div class="stack"><h2>{E(heading)}</h2><p class="lede">{E(text)}</p></div>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a>
<span>or call or text <span class="mono">{E(B["phone_display"])}</span></span></div>
</div></section>'''


def faq_html(items):
    return '<div class="faq">' + "".join(
        f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in items) + "</div>"


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def service_schema(ctx, svc):
    return {"@context": "https://schema.org", "@type": "Service",
            "name": f"{svc['name']} in Naples, FL", "serviceType": svc["name"],
            "provider": {"@id": B["domain"] + "/#business"},
            "areaServed": [{"@type": "City", "name": f"{a['name']}, FL"} for a in AREAS.values()],
            "offers": {"@type": "Offer", "priceCurrency": "USD", "price": str(from_price(svc)),
                       "description": "Starting price for a 2-bedroom, 2-bathroom home"},
            "url": ctx.canonical(svc["slug"])}


# ---------------------------------------------------------------------------
# Shared content
# ---------------------------------------------------------------------------
FAQ = [
    ("Do I need to be home during the clean?",
     "No. Many of our clients are at work or out of state. Leave a key in a lockbox or give us a door or gate code, and you'll get a photo report by text when the clean is done."),
    ("Are your cleaners background-checked and insured?",
     "Yes. Every cleaner passes a background check before entering a client's home, and every clean is covered by our general liability insurance. We can send a certificate of insurance to your HOA or condo association."),
    ("Do you bring cleaning supplies?",
     "Yes. Cleaners bring their own supplies and equipment. If you prefer a specific product, leave it out and we'll use it."),
    ("Will I get the same cleaner each time?",
     "We assign the same cleaner to recurring clients whenever possible. If they're out, a backup cleaner follows the same checklist and notes for your home."),
    ("What if I'm not happy with the clean?",
     "Tell us within 48 hours and we'll come back and re-clean the areas you flag, at no charge."),
    ("How do I pay?",
     "You save a card when you book, and it's charged after the clean is finished. There's nothing to pay in advance."),
    ("What is your cancellation policy?",
     "Reschedule or cancel at least 48 hours before your clean at no charge. Later cancellations may be charged a fee of up to half the clean."),
    ("Can you clean homes in gated communities and condo buildings?",
     "Yes. Give us the gate or building access instructions when you book. We'll send your association any vendor paperwork it requires before the first visit."),
    ("Can you look after my home while I'm away for the summer?",
     "We clean before you leave and before you return, and can add a mid-season refresh. We don't do home watch inspections, but we coordinate with your home watch company."),
    ("Do you clean homes with pets?",
     "Yes. Tell us about your pets when you book, and let us know if they should stay in a room or crate during the visit."),
]


def report_card(place="Pelican Bay"):
    return f'''<aside class="report" aria-label="Sample visit report">
<div class="report-head"><h2>Visit report</h2><span class="report-tag">Sample</span></div>
<dl><dt>Home</dt><dd>3 bed · 2 bath · {E(place)}</dd><dt>Arrived</dt><dd>9:02 AM</dd><dt>Finished</dt><dd>12:11 PM</dd><dt>Checklist</dt><dd>24 of 24</dd></dl>
<ul><li>Kitchen counters, stovetop and sink</li><li>Bathrooms scrubbed and disinfected</li><li>Floors vacuumed and mopped</li><li>Lanai furniture wiped down</li><li>Beds made with fresh linens</li></ul>
<div class="photos"><div class="photo">Kitchen</div><div class="photo">Bath</div><div class="photo">Lanai</div><div class="photo">Entry</div></div>
<p class="report-note">Every client gets a report like this by text after each clean.</p>
</aside>'''


def service_cards(ctx, exclude=None):
    cards = []
    for s in SERVICES:
        if s["slug"] == exclude:
            continue
        unit = "per turnover" if s["kind"] == "rental" else "per visit"
        cards.append(f'''<article class="card"><h3>{E(s["name"])}</h3><p>{E(s["blurb"])}</p>
<p class="price-from">From ${from_price(s)} {unit}</p><a class="more" href="{ctx.href(s["slug"])}">{E(s["name"])} details</a></article>''')
    return f'<div class="grid grid-services">{"".join(cards)}</div>'


def chips(zips):
    return '<ul class="chips">' + "".join(f"<li>{z}</li>" for z in zips) + "</ul>"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def home(ctx, wrapper=True):
    naples = AREAS["naples"]
    area_links = "".join(
        f'<li><a href="{ctx.href(k)}">{E(a["name"])}</a></li>' for k, a in AREAS.items() if k != "naples")
    body = f'''<section class="hero"><div class="wrap">
<div class="hero-copy">
<p class="eyebrow">Naples · Marco Island · Bonita Springs · Estero</p>
<h1>House cleaning in Naples, with <em>proof</em> after every visit</h1>
<p class="lede">Book a background-checked cleaner for your home or condo. When the clean is done, you get a photo report by text, whether you're down the street or 1,200 miles north for the summer.</p>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a>
<a class="btn btn-quiet" href="{ctx.href("pricing")}">See all prices</a></div>
<ul class="trust"><li>Prices shown upfront</li><li>Background-checked cleaners</li><li>Insured</li><li>Free re-clean within 48 hours</li></ul>
</div>
{report_card()}
</div></section>

<section class="section" id="services"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Services</p><h2>Cleaning for every kind of Naples home</h2>
<p class="lede">Year-round homes, seasonal homes, condos, rentals and empty homes between owners. Prices below are for a 2-bedroom, 2-bathroom home.</p></div>
{service_cards(ctx)}
</div></section>

<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">How it works</p><h2>Booked in a minute, confirmed by text</h2></div>
<ol class="steps">
<li><h3>Get your price</h3><p>Choose your home size and how often. The price you see is the price you pay.</p></li>
<li><h3>Pick a day</h3><p>We confirm by text and match you with a background-checked cleaner.</p></li>
<li><h3>We clean</h3><p>Your cleaner works through a room-by-room checklist for your home.</p></li>
<li><h3>You get the report</h3><p>Photos and the finished checklist arrive by text. Your card is charged after the clean.</p></li>
</ol>
</div></section>

<section class="band"><div class="wrap">
<div class="stack"><p class="eyebrow">Seasonal homes</p><h2>Leaving for the summer?</h2>
<p class="lede">We do a closing clean when you leave, an opening clean before you're back, and an optional mid-season refresh. You'll get photos after each one.</p></div>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("seasonal-home-cleaning")}">Seasonal home cleaning</a></div>
</div></section>

<section class="section" id="areas"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Service area</p><h2>Naples and the towns around it</h2>
<p class="lede">We clean throughout Naples, including {E(", ".join(naples["places"][:-1]))} and {E(naples["places"][-1])}, plus nearby towns.</p></div>
<div class="grid">
<div class="card"><h3>Naples zip codes</h3>{chips(naples["zips"])}</div>
<div class="card"><h3>Nearby towns</h3><ul class="prose">{area_links}</ul></div>
</div>
</div></section>

<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Questions</p><h2>Common questions</h2></div>
{faq_html(FAQ[:4])}
<p><a href="{ctx.href("faq")}">All questions and answers</a></p>
</div></section>
{cta_band(ctx)}'''
    return page(ctx, "index", "House Cleaning in Naples, FL | Sea Grape Home Cleaning",
                "Recurring, deep and move-out house cleaning in Naples, Marco Island, Bonita Springs and Estero. Upfront prices and a photo report after every visit.",
                body, active=None, schema=[business_schema(ctx), faq_schema(FAQ[:4])], wrapper=wrapper)


SERVICE_DETAIL = {
    "recurring-cleaning": {
        "title": "Recurring House Cleaning in Naples, FL | Sea Grape",
        "h1": "Recurring house cleaning in Naples",
        "lede": "Keep your home clean on a schedule: weekly, every two weeks or monthly. The same checklist every visit, a photo report after each one, and your card charged only after the clean.",
        "included": [
            ("Kitchen", "Counters, backsplash, stovetop, sink, outside of appliances, microwave inside and out, floors"),
            ("Bathrooms", "Toilets, showers, tubs, sinks, mirrors and fixtures scrubbed and disinfected, floors"),
            ("Bedrooms and living areas", "Dusting of reachable surfaces, beds made, floors vacuumed and mopped, trash out"),
            ("Lanai", "Furniture wiped down, floor swept (screened lanais)"),
        ],
        "who": "Year-round residents, busy families and retirees who want the house kept up without thinking about it.",
        "extra": "<h2>How often should I book?</h2><p>Every two weeks suits most homes. Weekly works best with kids or pets. Monthly keeps a quiet home or a lightly used condo in shape.</p>",
        "faq": [FAQ[3], FAQ[6], FAQ[5]],
    },
    "deep-cleaning": {
        "title": "Deep Cleaning in Naples, FL | Sea Grape Home Cleaning",
        "h1": "Deep cleaning in Naples",
        "lede": "A top-to-bottom clean for homes that need more than upkeep. Every recurring plan starts with one, so later visits keep the home at that level.",
        "included": [
            ("Everything in a standard clean", "Kitchen, bathrooms, bedrooms, living areas and lanai"),
            ("Detail work", "Baseboards, door frames, light switches, cabinet fronts, window sills and blinds"),
            ("Kitchen and bath detail", "Grout scrubbed, hard-water spots on glass and fixtures, range hood"),
            ("Add-ons", "Inside the fridge, inside the oven, interior windows"),
        ],
        "who": "New clients, homes that haven't been cleaned professionally in a while, and spring or holiday resets.",
        "extra": "<h2>How long does it take?</h2><p>A deep clean of a 3-bedroom, 2-bathroom home usually takes one cleaner about 5 hours. Larger homes get two cleaners.</p>",
        "faq": [FAQ[2], FAQ[4], FAQ[0]],
    },
    "move-out-cleaning": {
        "title": "Move-Out Cleaning in Naples, FL | Sea Grape Home Cleaning",
        "h1": "Move-in and move-out cleaning in Naples",
        "lede": "Empty-home cleaning timed to your closing, listing or lease end. You get a photo report you can send to the landlord, buyer or property manager.",
        "included": [
            ("Inside everything", "Cabinets, drawers, closets, shelves, fridge and oven"),
            ("Kitchen and bathrooms", "Full scrub and disinfect, grout, fixtures, mirrors"),
            ("Floors and trim", "Baseboards, door frames, vents, floors vacuumed and mopped"),
            ("Photo report", "Room-by-room photos sent the same day"),
        ],
        "who": "Homeowners selling, tenants getting a deposit back, realtors preparing listings, and property managers between tenants.",
        "extra": "<h2>For realtors and property managers</h2><p>We schedule around showings and closings, work from a lockbox, and send photos the same day. Ask about priority booking for repeat partners.</p>",
        "faq": [FAQ[0], FAQ[5], FAQ[4]],
    },
    "seasonal-home-cleaning": {
        "title": "Seasonal Home Cleaning in Naples, FL | Sea Grape",
        "h1": "Seasonal home cleaning for part-year residents",
        "lede": "Close your Naples home cleanly when you head north, and come back to a home that's ready. Photos after every visit, so you know it's done from wherever you are.",
        "included": [
            ("Closing clean", "Full clean, fridge emptied and wiped, beds stripped and linens laundered, trash out"),
            ("Opening clean", "Dusting after months closed, beds made, bathrooms refreshed, lanai furniture wiped"),
            ("Mid-season refresh", "Optional visit while you're away to keep dust and humidity marks down"),
            ("Coordination", "We work with your home watch company, gate and condo access instructions"),
        ],
        "who": "Seasonal residents in Naples, Marco Island, Bonita Springs and Estero.",
        "extra": "<h2>When to book</h2><p>Opening cleans fill up from October to December as residents return. Closing cleans are busiest from April to May. Book two to three weeks ahead in those months.</p>",
        "faq": [FAQ[8], FAQ[7], FAQ[0]],
    },
    "vacation-rental-cleaning": {
        "title": "Vacation Rental Cleaning in Naples & Marco Island | Sea Grape",
        "h1": "Vacation rental turnover cleaning",
        "lede": "Same-day turnovers between check-out and check-in for short-term rentals in Naples and Marco Island, with damage and supply photos sent to the host.",
        "included": [
            ("Turnover clean", "Kitchen, bathrooms, floors, trash out, beds made with the host's linens"),
            ("Guest-ready check", "Restock list checked against your inventory, staging photos"),
            ("Damage and supply photos", "Anything broken, missing or low is photographed and texted to you"),
            ("Scheduling", "Synced to your booking calendar on request"),
        ],
        "who": "Airbnb and VRBO hosts, co-hosts and rental managers.",
        "extra": "<h2>Linens</h2><p>We make beds with the host's linens. Laundry can be added per turnover.</p>",
        "faq": [FAQ[2], FAQ[4], FAQ[5]],
    },
}


def service_page(ctx, svc):
    d = SERVICE_DETAIL[svc["slug"]]
    trail = [("index", "Home"), (svc["slug"], svc["name"])]
    rows = "".join(f"<tr><td><strong>{E(a)}</strong></td><td>{E(b)}</td></tr>" for a, b in d["included"])
    if svc["kind"] == "rental":
        price_rows = "".join(f'<tr><td>{b} bed · {ba} bath</td><td class="num">${price("rental", b, ba)}</td></tr>' for b, ba in SIZES)
        price_head = "<tr><th>Home size</th><th>Per turnover</th></tr>"
    else:
        price_rows = "".join(f'<tr><td>{b} bed · {ba} bath</td><td class="num">${price(svc["kind"], b, ba)}</td></tr>' for b, ba in SIZES)
        price_head = "<tr><th>Home size</th><th>Per visit</th></tr>"
    body = f'''{crumbs_html(ctx, trail)}
<section class="hero"><div class="wrap">
<div class="hero-copy"><p class="eyebrow">{E(svc["name"])}</p><h1>{E(d["h1"])}</h1><p class="lede">{E(d["lede"])}</p>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a><span class="price-from">From ${from_price(svc)}</span></div></div>
{report_card()}
</div></section>
<section class="section"><div class="wrap stack-lg">
<div class="stack"><h2>What's included</h2></div>
<div class="table-scroll"><table><thead><tr><th>Area</th><th>What we do</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="grid">
<div class="card"><h3>Who it's for</h3><p>{E(d["who"])}</p></div>
<div class="card"><h3>Starting prices</h3><div class="table-scroll"><table><thead>{price_head}</thead><tbody>{price_rows}</tbody></table></div></div>
</div>
<div class="prose">{d["extra"]}</div>
</div></section>
<section class="section"><div class="wrap stack-lg"><h2>Questions</h2>{faq_html(d["faq"])}</div></section>
<section class="section"><div class="wrap stack-lg"><h2>Other services</h2>{service_cards(ctx, exclude=svc["slug"])}</div></section>
{cta_band(ctx)}'''
    return page(ctx, svc["slug"], d["title"],
                d["lede"][:155].rsplit(" ", 1)[0] + "." if len(d["lede"]) > 155 else d["lede"],
                body, active="services",
                schema=[service_schema(ctx, svc), breadcrumb_schema(ctx, trail), faq_schema(d["faq"])])


AREA_DETAIL = {
    "marco-island": {
        "title": "House Cleaning in Marco Island, FL | Sea Grape",
        "lede": "Condo, home and vacation rental cleaning on Marco Island, with a photo report after every visit.",
        "body": [
            "Much of Marco Island is condos, seasonal homes and short-term rentals, so most of our work here happens while owners are away. We work from lockboxes and building access instructions, and the photo report shows the result.",
            "Salt air and beach sand mean glass, lanai screens and tile floors need more attention here than inland. Our checklist for island homes covers sliding-door tracks, lanai furniture and entry floors on every visit.",
            "For condo buildings, we send the association's vendor paperwork and certificate of insurance before the first visit, and follow the building's rules on parking, elevators and service hours.",
        ],
        "services": ["vacation-rental-cleaning", "seasonal-home-cleaning", "recurring-cleaning"],
    },
    "bonita-springs": {
        "title": "House Cleaning in Bonita Springs, FL | Sea Grape",
        "lede": "Recurring, deep and seasonal house cleaning in Bonita Springs, with a photo report after every visit.",
        "body": [
            "Bonita Springs has many gated and golf communities and a large share of part-year residents. We set up gate access before the first visit so your cleaner isn't turned away at the gate.",
            "Year-round households usually book every two weeks. Seasonal owners book a closing clean in spring and an opening clean in the fall, often coordinated with their home watch company.",
            "Every clean follows the same room-by-room checklist, and you get photos by text when it's done.",
        ],
        "services": ["recurring-cleaning", "seasonal-home-cleaning", "deep-cleaning"],
    },
    "estero": {
        "title": "House Cleaning in Estero, FL | Sea Grape Home Cleaning",
        "lede": "Recurring and deep house cleaning in Estero, with prices shown upfront and a photo report after every visit.",
        "body": [
            "Estero is home to newer communities with working families as well as retirees. Most clients here book a deep clean first and then a clean every two weeks.",
            "Moving into a new build or out of a rental? Our move-in and move-out clean covers the inside of cabinets, closets and appliances, and comes with a photo report.",
            "We coordinate gate and community access before your first visit, and your card is charged only after the clean is done.",
        ],
        "services": ["recurring-cleaning", "deep-cleaning", "move-out-cleaning"],
    },
}


def area_page(ctx, key):
    a, d = AREAS[key], AREA_DETAIL[key]
    trail = [("index", "Home"), (key, a["name"])]
    svc_by_slug = {s["slug"]: s for s in SERVICES}
    cards = "".join(
        f'''<article class="card"><h3>{E(svc_by_slug[s]["name"])}</h3><p>{E(svc_by_slug[s]["blurb"])}</p>
<p class="price-from">From ${from_price(svc_by_slug[s])}</p><a class="more" href="{ctx.href(s)}">{E(svc_by_slug[s]["name"])} details</a></article>'''
        for s in d["services"])
    paras = "".join(f"<p>{E(p)}</p>" for p in d["body"])
    schema = business_schema(ctx) | {"areaServed": {"@type": "City", "name": f"{a['name']}, FL"}}
    body = f'''{crumbs_html(ctx, trail)}
<section class="hero"><div class="wrap">
<div class="hero-copy"><p class="eyebrow">{E(a["name"])}, Florida</p><h1>House cleaning in {E(a["name"])}</h1><p class="lede">{E(d["lede"])}</p>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a></div></div>
{report_card(a["name"])}
</div></section>
<section class="section"><div class="wrap stack-lg">
<div class="prose"><h2>Cleaning in {E(a["name"])}</h2>{paras}</div>
<div class="stack"><h3>Zip codes we serve</h3>{chips(a["zips"])}</div>
</div></section>
<section class="section"><div class="wrap stack-lg"><h2>Popular in {E(a["name"])}</h2><div class="grid">{cards}</div></div></section>
{cta_band(ctx)}'''
    return page(ctx, key, d["title"], d["lede"], body, active="areas",
                schema=[schema, breadcrumb_schema(ctx, trail)])


def pricing_page(ctx):
    trail = [("index", "Home"), ("pricing", "Pricing")]
    head = "".join(f"<th>{b} bed · {ba} bath</th>" for b, ba in SIZES)
    rows = [("Weekly clean", "weekly"), ("Every-two-weeks clean", "biweekly"), ("Monthly clean", "monthly"),
            ("One-time standard clean", "onetime"), ("Deep clean", "deep"),
            ("Move-in or move-out clean", "moveout"), ("Seasonal opening or closing clean", "seasonal"),
            ("Vacation rental turnover", "rental")]
    body_rows = "".join(
        f"<tr><td>{E(n)}</td>" + "".join(f'<td class="num">${price(k, b, ba)}</td>' for b, ba in SIZES) + "</tr>"
        for n, k in rows)
    addons = "".join(f'<tr><td>{E(n)}</td><td class="num">${p}</td></tr>' for _, n, p in ADDONS)
    body = f'''{crumbs_html(ctx, trail)}
<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Pricing</p><h1>House cleaning prices in Naples</h1>
<p class="lede">Prices depend on your home's bedrooms and bathrooms and how often you book. Your card is charged after each clean.</p></div>
<div class="table-scroll"><table><thead><tr><th>Service</th>{head}</tr></thead><tbody>{body_rows}</tbody></table></div>
<p>Homes over 5 bedrooms or 4,000 square feet get a custom quote. Recurring plans start with a deep clean on the first visit.</p>
<div class="grid">
<div class="card"><h2 class="h3">Add-ons</h2><div class="table-scroll"><table><tbody>{addons}</tbody></table></div></div>
<div class="card"><h2 class="h3">Not included</h2><ul class="prose"><li>Exterior windows and pressure washing</li><li>Biohazards, mold remediation or pest cleanup</li><li>Moving heavy furniture</li><li>Post-construction debris</li></ul></div>
<div class="card"><h2 class="h3">Policies</h2><ul class="prose"><li>Charged after the clean, never before</li><li>Free reschedule with 48 hours' notice</li><li>Free re-clean if you flag a problem within 48 hours</li></ul></div>
</div>
</div></section>
{cta_band(ctx)}'''
    return page(ctx, "pricing", "House Cleaning Prices in Naples, FL | Sea Grape",
                "See house cleaning prices in Naples by home size: weekly, every-two-weeks, deep, move-out, seasonal and vacation rental cleaning.",
                body, active="pricing", schema=[breadcrumb_schema(ctx, trail)])


def faq_page(ctx):
    trail = [("index", "Home"), ("faq", "FAQ")]
    body = f'''{crumbs_html(ctx, trail)}
<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">FAQ</p><h1>Questions about house cleaning in Naples</h1></div>
{faq_html(FAQ)}
</div></section>
{cta_band(ctx)}'''
    return page(ctx, "faq", "House Cleaning FAQ | Sea Grape Home Cleaning, Naples FL",
                "Answers about our Naples house cleaning: access while you're away, insurance, supplies, payment, cancellations and gated communities.",
                body, active="faq", schema=[faq_schema(FAQ), breadcrumb_schema(ctx, trail)])


def about_page(ctx):
    trail = [("index", "Home"), ("about", "About")]
    body = f'''{crumbs_html(ctx, trail)}
<section class="section"><div class="wrap stack-lg">
<div class="prose">
<p class="eyebrow">About</p>
<h1>A Naples cleaning company built around proof</h1>
<p class="lede">Many Naples homeowners aren't home when their house gets cleaned. They're at work, at the club, or up north for the summer. We built Sea Grape so they can still see that the job was done right.</p>
<p>Every clean follows a written, room-by-room checklist for that home. When the cleaner finishes, the client gets photos and the completed checklist by text. Payment happens after the clean, not before.</p>
<p>Our cleaners are background-checked before their first visit, and every clean is insured. If something isn't right, tell us within 48 hours and we'll come back to fix it at no charge.</p>
<p>We're named after the sea grape, the round-leafed shrub that grows along Southwest Florida's beaches and holds the dunes in place.</p>
</div>
</div></section>
{cta_band(ctx)}'''
    return page(ctx, "about", "About Sea Grape Home Cleaning | Naples, FL",
                "Sea Grape is a Naples-area house cleaning company: checklist cleans, photo reports after every visit, and payment after the clean.",
                body, active="about", schema=[breadcrumb_schema(ctx, trail)])


ESTIMATOR_JS = """
(() => {
  const P = __PRICING__;
  const f = document.getElementById('estimate-form');
  const out = document.getElementById('quote-total');
  const label = document.getElementById('quote-label');
  const go = document.getElementById('quote-go');
  const r5 = x => Math.floor(x / 5 + 0.5) * 5;
  const names = {weekly: 'Weekly clean', biweekly: 'Every-two-weeks clean', monthly: 'Monthly clean', onetime: 'One-time clean',
    deep: 'Deep clean', moveout: 'Move-in or move-out clean', seasonal: 'Seasonal opening or closing clean', rental: 'Rental turnover'};
  function calc() {
    const bed = +f.bedrooms.value, bath = +f.bathrooms.value, kind = f.service.value;
    let total = kind === 'rental' ? r5(P.rentalFixed + P.rentalPerRoom * (bed + bath))
      : r5((P.fixed + P.perBed * bed + P.perBath * bath) * P.mult[kind]);
    P.addons.forEach(a => { const el = document.getElementById('addon-' + a.id); if (el && el.checked) total += a.price; });
    out.textContent = '$' + total;
    label.textContent = names[kind] + ', ' + bed + ' bed · ' + bath + ' bath';
  }
  f.addEventListener('input', calc);
  f.addEventListener('change', calc);
  f.addEventListener('submit', e => { e.preventDefault(); if (go) go.focus(); });
  calc();
})();
"""


def book_page(ctx):
    trail = [("index", "Home"), ("book", "Get your price")]
    pricing = {"fixed": BASE_FIXED, "perBed": PER_BED, "perBath": PER_BATH, "mult": MULT,
               "rentalFixed": RENTAL_FIXED, "rentalPerRoom": RENTAL_PER_ROOM,
               "addons": [{"id": i, "price": p} for i, _, p in ADDONS]}
    beds = "".join(f'<option value="{n}"{" selected" if n == 3 else ""}>{n}</option>' for n in range(1, 7))
    baths = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n}</option>' for n in range(1, 6))
    svc_opts = [("biweekly", "Every two weeks"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("onetime", "One time"),
                ("deep", "Deep clean"), ("moveout", "Move-in / move-out"), ("seasonal", "Seasonal open / close"),
                ("rental", "Rental turnover")]
    seg = "".join(
        f'<label><input type="radio" name="service" id="svc-{k}" value="{k}"{" checked" if k == "biweekly" else ""}><span>{E(n)}</span></label>'
        for k, n in svc_opts)
    addons = "".join(
        f'<label class="seg"><input type="checkbox" id="addon-{i}" name="addon-{i}"><span>{E(n)} +${p}</span></label>'
        for i, n, p in ADDONS)
    js = ESTIMATOR_JS.replace("__PRICING__", json.dumps(pricing))
    body = f'''{crumbs_html(ctx, trail)}
<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Get your price</p><h1>See your price, then book</h1>
<p class="lede">Choose your home size and the kind of clean. The price updates as you go.</p></div>
<div class="estimator">
<form id="estimate-form" class="stack" novalidate>
<div class="grid">
<div class="field"><label for="bedrooms">Bedrooms</label><select id="bedrooms" name="bedrooms">{beds}</select></div>
<div class="field"><label for="bathrooms">Bathrooms</label><select id="bathrooms" name="bathrooms">{baths}</select></div>
</div>
<fieldset><legend>Type of clean</legend><div class="seg">{seg}</div></fieldset>
<fieldset><legend>Add-ons</legend><div class="seg">{addons}</div></fieldset>
</form>
<aside class="quote" aria-live="polite">
<small id="quote-label">Every-two-weeks clean</small>
<div class="quote-total" id="quote-total">$185</div>
<small>Charged after the clean. First recurring visit is a deep clean.</small>
<a class="btn btn-primary" id="quote-go" href="{E(B["booking_url"])}">Choose a day</a>
<small>Prefer to talk? Call or text <span class="mono">{E(B["phone_display"])}</span>, {E(B["hours"])}.</small>
</aside>
</div>
</div></section>
<script>{js}</script>'''
    return page(ctx, "book", "Get a House Cleaning Price | Sea Grape, Naples FL",
                "Get an instant house cleaning price for your Naples, Marco Island, Bonita Springs or Estero home, then pick a day.",
                body, active=None, schema=[breadcrumb_schema(ctx, trail)])


def not_found(ctx):
    body = f'''<section class="section"><div class="wrap stack">
<h1>Page not found</h1><p class="lede">That page doesn't exist. Try the home page or get your price.</p>
<div class="btn-row"><a class="btn btn-primary" href="{ctx.href("book")}">Get your price</a><a class="btn btn-quiet" href="{ctx.href("index")}">Home</a></div>
</div></section>'''
    return page(ctx, "404", "Page not found | Sea Grape Home Cleaning", "Page not found.", body, noindex=True)


# ---------------------------------------------------------------------------
# Brand kit
# ---------------------------------------------------------------------------
BRAND = {
    "taglines": ["Clean homes, with proof.", "Naples homes, cleaned and photographed.",
                 "See it's done, wherever you are."],
    "positioning": ("For Naples-area homeowners who aren't always home, Sea Grape is the house cleaning company "
                    "that proves every clean with photos and a finished checklist, and charges only after the job is done."),
    "audiences": [
        ("Seasonal owners", "Part-year residents who need a closing clean, an opening clean and proof from out of state."),
        ("Year-round households", "Working families and retirees who want a reliable every-two-weeks clean."),
        ("Realtors and property managers", "Move-out and listing-prep cleans on short notice, with photos for the file."),
        ("Rental hosts", "Turnovers on Marco Island and in Naples, with damage and supply photos."),
    ],
    "voice_do": ["Say exactly what's included and what it costs", "Use plain, calm sentences",
                 "Show proof: photos, checklists, policies", "Name real places: Pelican Bay, Marco Island, Estero"],
    "voice_dont": ["Claim results you can't show", "Use 'sparkling', 'spotless' or 'maids'",
                   "Post reviews or before-and-after photos without the client's written permission",
                   "Promise availability you don't have"],
    "colors": [
        ("Leaf", "#2E6B57", "#7CC2A8", "Primary brand color: logo, links, headings accents"),
        ("Leaf deep", "#1F4D3F", "#A9D9C6", "Footer, uniforms, vehicle magnets"),
        ("Sea grape plum", "#6A3D6E", "#D2A8D6", "The one action: Book, Get your price"),
        ("Gulf water", "#DCEFEB", "#17312C", "Soft background bands"),
        ("Mangrove ink", "#13241F", "#E6EFEC", "Body text"),
        ("Shell", "#F5F8F6", "#0F1A17", "Page background"),
    ],
    "type": [
        ("Bricolage Grotesque", "Headlines, logo wordmark", "600–800"),
        ("Atkinson Hyperlegible", "Body text, buttons. Built for legibility, which matters for older readers", "400, 700"),
        ("IBM Plex Mono", "Prices, times, zip codes, labels", "400, 500"),
    ],
    "gbp_description": ("Sea Grape Home Cleaning provides recurring, deep, move-in and move-out, seasonal and vacation rental "
                        "cleaning for homes and condos in Naples, Marco Island, Bonita Springs and Estero. Every clean follows "
                        "a room-by-room checklist, and clients get a photo report by text when the clean is done, so you can "
                        "see your home is cleaned even when you're away. Prices are shown upfront on our website, cleaners are "
                        "background-checked, every clean is insured, and your card is charged only after the clean. Seasonal "
                        "residents can book a closing clean before heading north and an opening clean before they return. "
                        "Call or text to book."),
    "bio": "House cleaning in Naples, Marco Island, Bonita Springs and Estero. Photo report after every clean. Prices upfront.",
    "texts": [
        ("Missed call", "Thanks for calling Sea Grape Home Cleaning! Want a quote? Reply with your bedrooms, bathrooms and zip code, or see prices at seagrapecleaning.com."),
        ("Booking confirmed", "You're booked for {day} at {time}. Your cleaner is {name}. We'll text the night before and send a photo report when we're done."),
        ("Review request (after 2nd clean)", "Thanks for having us again! If you're happy with your cleans, a Google review helps a small local business a lot: {link}"),
    ],
}


def brand_kit_page(ctx):
    sw = "".join(
        f'''<div class="swatch"><div class="swatch-color" style="background:{light}"></div>
<div><strong>{E(n)}</strong><span class="mono">{light} · dark {dark}</span><span>{E(use)}</span></div></div>'''
        for n, light, dark, use in BRAND["colors"])
    types = "".join(f"<tr><td><strong>{E(n)}</strong></td><td>{E(u)}</td><td class=\"num\">{E(w)}</td></tr>" for n, u, w in BRAND["type"])
    aud = "".join(f'<div class="card"><h3>{E(n)}</h3><p>{E(d)}</p></div>' for n, d in BRAND["audiences"])
    do = "".join(f"<li>{E(x)}</li>" for x in BRAND["voice_do"])
    dont = "".join(f"<li>{E(x)}</li>" for x in BRAND["voice_dont"])
    tags = "".join(f"<li>{E(x)}</li>" for x in BRAND["taglines"])
    texts = "".join(f"<tr><td><strong>{E(n)}</strong></td><td>{E(t)}</td></tr>" for n, t in BRAND["texts"])
    body = f'''<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Brand kit</p><h1>Sea Grape Home Cleaning</h1><p class="lede">{E(BRAND["positioning"])}</p></div>
<div class="grid">
<div class="card" style="place-items:center;padding:2rem">{logo_svg(120)}<p class="mono">Mark</p></div>
<div class="card" style="align-content:center;padding:2rem"><div class="brand" style="margin:0">{logo_svg(56, label=False)}<span class="brand-name" style="font-size:1.8rem">Sea Grape<small>Home Cleaning</small></span></div><p class="mono">Horizontal lockup</p></div>
<div class="card"><h3>Logo rules</h3><ul class="prose"><li>Clear space around the logo: at least one grape's width</li><li>Smallest size: 24 px tall on screen, 0.5 in printed</li><li>On dark backgrounds, use the light-leaf version</li><li>Don't stretch, recolor or add effects</li></ul></div>
</div>
<div class="stack"><h2>Colors</h2><div class="swatches">{sw}</div></div>
<div class="stack"><h2>Type</h2><div class="table-scroll"><table><thead><tr><th>Typeface</th><th>Use</th><th>Weights</th></tr></thead><tbody>{types}</tbody></table></div></div>
<div class="stack"><h2>Taglines</h2><ul class="prose">{tags}</ul></div>
<div class="stack"><h2>Who we serve</h2><div class="grid">{aud}</div></div>
<div class="grid"><div class="card"><h3>Voice: do</h3><ul class="prose">{do}</ul></div><div class="card"><h3>Voice: don't</h3><ul class="prose">{dont}</ul></div></div>
<div class="stack"><h2>Google Business Profile description</h2><p class="prose">{E(BRAND["gbp_description"])}</p><p class="mono" style="font-size:.85rem">{len(BRAND["gbp_description"])} of 750 characters</p></div>
<div class="stack"><h2>Social bio</h2><p>{E(BRAND["bio"])}</p></div>
<div class="stack"><h2>Text templates for Quo</h2><div class="table-scroll"><table><tbody>{texts}</tbody></table></div></div>
<div class="stack"><h2>Photography</h2><ul class="prose"><li>Real client homes in daylight, with written permission. No stock photos of smiling maids.</li><li>Show the result: a made bed, a clear counter, a wiped lanai table.</li><li>Never show house numbers, faces or anything that identifies a client's home.</li></ul></div>
</div></section>'''
    return page(ctx, "brand-kit", "Sea Grape Brand Kit", "Logo, colors, type, voice and copy for Sea Grape Home Cleaning.",
                body, noindex=True)


def brand_md():
    lines = ["# Sea Grape Home Cleaning — brand kit", "",
             "Generated by `site/build.py`. Edit the `BRAND` data there, then rebuild.", "",
             "## Positioning", "", BRAND["positioning"], "", "## Taglines", ""]
    lines += [f"- {t}" for t in BRAND["taglines"]]
    lines += ["", "## Who we serve", ""] + [f"- **{n}:** {d}" for n, d in BRAND["audiences"]]
    lines += ["", "## Logo", "",
              "- `brand/logo-mark.svg`: the sea grape leaf and fruit, for favicons, social avatars and stickers",
              "- `brand/logo-horizontal.svg`: mark plus wordmark. The wordmark uses Bricolage Grotesque; outline the text in Figma or Canva before sending to a printer",
              "- Clear space: at least one grape's width on every side",
              "- Smallest size: 24 px tall on screen, 0.5 in printed",
              "- Don't stretch, recolor or add effects", "", "## Colors", "",
              "| Name | Light | Dark mode | Use |", "| --- | --- | --- | --- |"]
    lines += [f"| {n} | `{l}` | `{d}` | {u} |" for n, l, d, u in BRAND["colors"]]
    lines += ["", "## Type (all free on Google Fonts)", "", "| Typeface | Use | Weights |", "| --- | --- | --- |"]
    lines += [f"| {n} | {u} | {w} |" for n, u, w in BRAND["type"]]
    lines += ["", "## Voice", "", "Do:", ""] + [f"- {x}" for x in BRAND["voice_do"]]
    lines += ["", "Don't:", ""] + [f"- {x}" for x in BRAND["voice_dont"]]
    lines += ["", "## Google Business Profile description", "",
              f"({len(BRAND['gbp_description'])} of 750 characters)", "", BRAND["gbp_description"],
              "", "## Social bio", "", BRAND["bio"], "", "## Text templates for Quo", ""]
    lines += [f"- **{n}:** {t}" for n, t in BRAND["texts"]]
    lines += ["", "## Photography", "",
              "- Real client homes in daylight, with written permission. No stock photos of smiling maids.",
              "- Show the result: a made bed, a clear counter, a wiped lanai table.",
              "- Never show house numbers, faces or anything that identifies a client's home.", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Launch checklist (SEO + other channels)
# ---------------------------------------------------------------------------
CHECKLIST = [
    ("Before the site goes live", [
        ("Check the name", "Search Sunbiz, the USPTO trademark search and Google Maps for 'Sea Grape' cleaning in Florida. Pick another name if there's a conflict."),
        ("Buy the domain", "Check seagrapecleaning.com; if taken, try seagrapehomecleaning.com. Use the same name everywhere."),
        ("Replace placeholders", "Phone, email, domain and booking link at the top of site/build.py, then run python3 site/build.py."),
        ("Make every claim true first", "Bind insurance and background-check cleaners before the site says 'insured' and 'background-checked'."),
        ("Host it", "Connect the repo to Cloudflare Pages: no build command, output folder site/public. Add the custom domain."),
    ]),
    ("Technical SEO", [
        ("Google Search Console", "Verify the domain and submit /sitemap.xml."),
        ("Bing Webmaster Tools", "Import from Search Console. Bing also feeds some AI search answers."),
        ("Analytics", "Add Google Analytics 4 or Cloudflare Web Analytics. Track clicks on 'Choose a day' and the phone number."),
        ("Speed and mobile", "Run PageSpeed Insights on the home and book pages; aim for 90+ on mobile."),
        ("Structured data", "Test the home page in Google's Rich Results Test (LocalBusiness, FAQ, Breadcrumbs are built in)."),
    ]),
    ("Google Business Profile (the main local SEO lever)", [
        ("Create it as a service-area business", "Hide the address. Service areas: Naples, Marco Island, Bonita Springs, Estero."),
        ("Verification", "Google needs a real address it can verify. A mailbox or virtual office gets suspended. Plan for a staffed coworking desk or a local manager's workplace."),
        ("Categories", "Primary: House cleaning service. Add only categories you actually offer."),
        ("Services and prices", "List all 5 services with 'from' prices that match the website."),
        ("Description", "Paste the 750-character description from the brand kit."),
        ("Photos", "Logo, cover, and real (permitted) result photos. Add new ones weekly."),
        ("Posts", "One post a week: a seasonal tip, an offer or a finished job (with permission)."),
        ("Reviews", "Text the review link after each client's 2nd clean. Reply to every review within 24 hours."),
    ]),
    ("Citations (same name and phone everywhere)", [
        ("Apple Business Connect", "Shows your business in Apple Maps and Siri."),
        ("Bing Places", "Import from Google Business Profile."),
        ("Yelp, Nextdoor business page, Facebook page", "Same name, phone, hours and service area."),
        ("Angi and Thumbtack", "Free profiles; pay-per-lead is optional, so test with a small budget."),
        ("Local chambers", "Consider the Greater Naples, Marco Island and Bonita Springs chambers for directory links and referrals."),
    ]),
    ("Reviews and reputation", [
        ("Goal", "10 Google reviews in the first 60 days."),
        ("Ask the right way", "Ask every client; never pay for reviews, offer discounts for good ones, or post fake ones. The FTC's rule on fake reviews applies to small businesses too."),
        ("Respond", "Thank every reviewer; answer complaints with the fix you made."),
    ]),
    ("Content (one useful page or post a month)", [
        ("Seasonal closing checklist", "What to do before leaving Naples for the summer, and what a closing clean covers."),
        ("Move-out checklist for Naples rentals", "What landlords inspect, for tenants trying to get a deposit back."),
        ("Cleaning in gated communities and condos", "Vendor paperwork, insurance certificates and access."),
        ("Hurricane-season prep and cleanup", "What to do before a storm, and the cleaning that follows."),
    ]),
    ("Partnerships (Naples-specific, usually the fastest clients)", [
        ("Realtors", "Move-out and listing-prep cleans. Offer same-week booking and a photo report for the file."),
        ("Property managers and condo management companies", "Get on their vendor list; have your certificate of insurance ready."),
        ("Home watch companies", "They look after seasonal homes but don't clean. Trade referrals for opening and closing cleans."),
        ("Vacation rental managers on Marco Island", "Turnover contracts with photo reports."),
        ("Movers and pool or lawn services", "Swap referrals with services that already visit your clients' homes."),
    ]),
    ("Paid channels (after insurance, background checks and 5 reviews)", [
        ("Google Local Services Ads", "Usually the best paid channel for cleaning. Requires business and owner checks plus insurance."),
        ("Google Search ads", "Only if Local Services Ads aren't available; target 'house cleaning Naples' terms."),
        ("Meta and Nextdoor ads", "Target Collier County and southern Lee County homeowners. Lead with the seasonal offer in October–November and April–May."),
    ]),
    ("Social", [
        ("Instagram and Facebook", "Result photos (with permission), short checklist videos, seasonal tips. Use the bio from the brand kit."),
        ("X (build in public)", "Optional: the real-numbers account from the earlier plan, linking back to the site."),
    ]),
    ("Tracking", [
        ("One phone number", "The same Quo number on the site, Google Business Profile and every listing."),
        ("Lead source", "Ask 'How did you hear about us?' on every booking and log it in the booking app."),
        ("Weekly scorecard", "Leads, bookings, cost per new client, reviews, recurring clients."),
    ]),
    ("Naples season calendar", [
        ("October–December", "Opening cleans as seasonal residents return. Push the seasonal offer hardest now."),
        ("January–April", "Peak season: recurring cleans and vacation rental turnovers."),
        ("April–May", "Closing cleans as residents leave. Offer a closing-plus-opening bundle."),
        ("June–September", "Move-outs, rentals and year-round clients. Hurricane season: have a reschedule policy ready."),
    ]),
]


def checklist_page(ctx):
    sections = []
    n = 0
    for title, items in CHECKLIST:
        lis = []
        for name, detail in items:
            n += 1
            lis.append(f'<li><input type="checkbox" id="c{n}" aria-label="{E(name)}"><span><strong>{E(name)}</strong><small>{E(detail)}</small></span></li>')
        sections.append(f'<div class="stack"><h2>{E(title)}</h2><ul class="check">{"".join(lis)}</ul></div>')
    body = f'''<section class="section"><div class="wrap stack-lg">
<div class="stack"><p class="eyebrow">Launch checklist</p><h1>SEO and channels for Naples</h1>
<p class="lede">Work top to bottom. Ticks here are only saved on this screen; the copy in the repo is docs/seo-and-channels-checklist.md.</p></div>
{"".join(sections)}
</div></section>'''
    return page(ctx, "checklist", "Sea Grape Launch Checklist", "SEO and marketing channel checklist for Sea Grape Home Cleaning in Naples.",
                body, noindex=True)


def checklist_md():
    lines = ["# Sea Grape Home Cleaning — SEO and channels checklist (Naples, FL)", "",
             "Generated by `site/build.py`. Edit the `CHECKLIST` data there, then rebuild.", ""]
    for title, items in CHECKLIST:
        lines += [f"## {title}", ""] + [f"- [ ] **{n}.** {d}" for n, d in items] + [""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def all_pages(ctx):
    pages = {"index": home(ctx), "pricing": pricing_page(ctx), "faq": faq_page(ctx), "about": about_page(ctx),
             "book": book_page(ctx), "404": not_found(ctx)}
    for s in SERVICES:
        pages[s["slug"]] = service_page(ctx, s)
    for k in AREA_DETAIL:
        pages[k] = area_page(ctx, k)
    return pages


def sitemap(ctx, slugs):
    urls = "".join(f"<url><loc>{ctx.canonical(s)}</loc></url>" for s in slugs if s != "404")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build():
    static = ROOT / "static"
    favicon = LOGO_FILE_SVG

    # Live site
    out = ROOT / "public"
    shutil.rmtree(out, ignore_errors=True)
    ctx = Ctx(preview=False)
    pages = all_pages(ctx)
    for slug, text in pages.items():
        write(out / f"{slug}.html", text)
    write(out / "sitemap.xml", sitemap(ctx, pages))
    write(out / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {B['domain']}/sitemap.xml\n")
    shutil.copy(static / "styles.css", out / "styles.css")
    write(out / "favicon.svg", favicon)
    write(out / "logo.svg", LOGO_FILE_SVG)

    # Preview (relative links, placeholder banner, brand kit and checklist pages)
    prev = ROOT / "preview"
    shutil.rmtree(prev, ignore_errors=True)
    pctx = Ctx(preview=True)
    ppages = all_pages(pctx)
    ppages["home"] = ppages.pop("index")
    ppages["brand-kit"] = brand_kit_page(pctx)
    ppages["checklist"] = checklist_page(pctx)
    for slug, text in ppages.items():
        write(prev / f"{slug}.html", text)
    entry = home(pctx, wrapper=False).replace(  # artifact entry page: no document wrapper, kit name as title
        "<title>House Cleaning in Naples, FL | Sea Grape Home Cleaning</title>", "<title>Sea Grape Launch Kit</title>", 1)
    write(prev / "index.html", entry)
    shutil.copy(static / "styles.css", prev / "styles.css")
    write(prev / "favicon.svg", favicon)

    # Brand files and docs
    write(REPO / "brand" / "logo-mark.svg", LOGO_FILE_SVG)
    write(REPO / "brand" / "logo-horizontal.svg", LOGO_HORIZONTAL_SVG)
    write(REPO / "brand" / "BRAND.md", brand_md())
    write(REPO / "docs" / "seo-and-channels-checklist.md", checklist_md())
    print(f"Built {len(pages)} live pages and {len(ppages) + 1} preview pages.")


if __name__ == "__main__":
    build()
