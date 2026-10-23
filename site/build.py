#!/usr/bin/env python3
"""Build the Clean by Morning website.

Usage:  python3 site/build.py

Writes:
  site/public/   the live website (deploy this folder to Cloudflare Pages)
  site/preview/  a flat preview copy with relative links (not committed)

Everything marked PLACEHOLDER must be replaced before launch. Proof (insurance, reviews, client names)
only appears once the matching setting below is filled in with something real.
"""
import html
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
E = html.escape

# ---------------------------------------------------------------------------
# Business settings
# ---------------------------------------------------------------------------
B = {
    "name": "Clean by Morning",
    "legal_name": "Clean by Morning Office Cleaning",
    "domain": "https://www.cleanbymorning.com",
    "phone_display": "(917) 555-0142",      # PLACEHOLDER: your business line
    "phone_e164": "+19175550142",           # PLACEHOLDER
    "email": "hello@cleanbymorning.com",    # set up this mailbox on the domain
    "city_line": "New York, NY",
    "office_hours": "Quotes Mon–Sat, 9 AM–7 PM",
    "cleaning_hours": "We clean after you close, 6 PM–2 AM",
    "hours_schema": ["Mo-Sa 09:00-19:00"],
    "form_endpoint": "",    # e.g. a Formspree or Basin URL; empty = the form opens a pre-filled email instead
    "ga4_id": "",           # Google Analytics 4 id, e.g. "G-XXXXXXX"
    "year": 2026,
    "same_as": [],          # Google Business Profile, LinkedIn, Instagram once they exist
}

PROOF = {
    "insured": False,            # True once general liability is bound (and you can send a certificate)
    "bonded": False,             # True once a janitorial bond is in place
    "workers_comp": False,       # True once you carry workers' comp (required from your first employee in NY)
    "review_count": 0, "rating": None, "google_reviews_url": "",
    "clients": [],               # client names you have written permission to list, e.g. "Park Slope Family Dental"
}

# ---------------------------------------------------------------------------
# Pricing: one model for the estimator, the price sentence, the pricing table and the schema
# ---------------------------------------------------------------------------
PRICING = {
    "hourly": 50,                  # charged per cleaning hour
    "min_visit": 75,               # minimum per visit
    "sqft_per_hour": {"medical": 1800, "dental": 1800, "office": 2500, "gym": 2000},
    "restroom_hours": 0.15,        # added per restroom per visit
    "weeks_per_month": 4.33,
    "postcon_per_sqft": 0.30, "postcon_min": 400, "deposit": 0.5,
}


def r5(x):
    return int(math.floor(x / 5 + 0.5) * 5)


def visit_price(kind, sqft, restrooms):
    hrs = sqft / PRICING["sqft_per_hour"][kind] + restrooms * PRICING["restroom_hours"]
    return max(PRICING["min_visit"], r5(hrs * PRICING["hourly"]))


def monthly_price(kind, sqft, restrooms, nights):
    return r5(visit_price(kind, sqft, restrooms) * nights * PRICING["weeks_per_month"])


def postcon_price(sqft):
    return max(PRICING["postcon_min"], r5(sqft * PRICING["postcon_per_sqft"]))


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
PHOTOS = {
    "bridge": {"file": "brooklyn-bridge-lower-manhattan-night.webp", "w": 1800, "h": 1200, "alt": "The Brooklyn Bridge and Lower Manhattan lit up at night"},
    "windows": {"file": "lit-office-windows-at-night.webp", "w": 1600, "h": 1067, "alt": "Rows of lit office windows on a tower at night"},
    "morning": {"file": "morning-at-office-windows.webp", "w": 1600, "h": 1067, "alt": "People at tall office windows looking over the city in the morning"},
    "rain": {"file": "rain-on-window-city-lights.webp", "w": 1400, "h": 875, "alt": "Rain on a window with city lights behind it at dusk"},
}
CREDITS = "Photos: Oleg Chursin, Vladimir Kudinov, Charles Forerunner and Riley Briggs, via Unsplash."

SERVICES = [
    {"key": "medical", "slug": "medical-office-cleaning", "name": "Medical office cleaning", "kind": "medical",
     "h1": "Medical office cleaning in NYC", "title": "Medical Office Cleaning NYC & Long Island | Clean by Morning",
     "lead": "Evening cleaning for medical practices in Brooklyn, Manhattan and Nassau County, done to a written checklist and finished before your first patient.",
     "nightly": ["Exam rooms: counters, chairs, door handles and light switches disinfected", "Waiting room: seats, front desk and touch points wiped; floors vacuumed and mopped",
                 "Restrooms scrubbed and disinfected; paper and soap restocked", "Trash and recycling out to your building's area", "Hard floors damp-mopped with a clean head for every area",
                 "Break room: counters, sink, microwave and fridge front"],
     "clinical": ["Color-coded microfiber: restroom cloths never touch exam rooms", "EPA-registered disinfectants, left wet for the label's contact time",
                  "We never handle sharps containers or regulated medical waste; those stay with your licensed hauler", "We don't open files, drawers or screens. Patient information stays where you left it"],
     "faq": [("Do you clean exam rooms every night?", "Yes. Every exam room on the schedule gets its surfaces and touch points disinfected each visit."),
             ("Do you handle medical waste?", "No. Sharps containers and regulated medical waste are handled by your licensed medical waste hauler. We empty regular trash and recycling only."),
             ("Which disinfectants do you use?", "EPA-registered hospital disinfectants, applied and left wet for the contact time on the label. If your practice has a required product, we'll use it.")]},
    {"key": "dental", "slug": "dental-office-cleaning", "name": "Dental office cleaning", "kind": "dental",
     "h1": "Dental office cleaning in NYC", "title": "Dental Office Cleaning NYC & Long Island | Clean by Morning",
     "lead": "Nightly cleaning for dental practices: operatory floors and surfaces outside the clinical zone, sterilization-area floors, reception and restrooms.",
     "nightly": ["Operatories: floors, counters outside the clinical zone, door handles and switches", "Sterilization area floors and sinks",
                 "Reception: front desk, chairs and the coffee or water station", "Restrooms scrubbed, disinfected and restocked",
                 "Trash and recycling out", "Hard floors damp-mopped; carpets vacuumed"],
     "clinical": ["We clean around dental chairs and equipment without moving or switching anything on", "Your clinical team keeps chairside surface disinfection between patients; we do the room",
                  "Color-coded microfiber and EPA-registered disinfectants", "We never handle sharps, amalgam or regulated waste"],
     "faq": [("Do you disinfect the dental chairs?", "Chairside surfaces between patients stay with your clinical team. At night we clean the operatory floors, counters outside the clinical zone and every touch point."),
             ("Can you clean after late appointments?", "Yes. We schedule around your last appointment, including late evenings."),
             ("How many nights a week do dental offices need?", "Most practices book three to five nights. The estimator shows the price for each.")]},
    {"key": "office", "slug": "office-cleaning", "name": "Office cleaning", "kind": "office",
     "h1": "Office cleaning in NYC", "title": "Office Cleaning NYC & Long Island | Clean by Morning",
     "lead": "Evening office cleaning for small and mid-size offices: desks, kitchens, restrooms and floors, ready before your team arrives.",
     "nightly": ["Desks and work surfaces wiped where clear", "Kitchen: counters, sink, microwave, appliance fronts", "Restrooms scrubbed and restocked",
                 "Trash and recycling out", "Floors vacuumed and mopped", "Doors, handles, switches and glass smudges"],
     "clinical": ["Same cleaner and checklist each night whenever possible", "Keys and alarm codes stored securely; we arm the alarm when we leave",
                  "Photos texted after the clean, if you want them", "Supplies included; restroom paper and soap restocked at cost"],
     "faq": [("Do you clean desks?", "We wipe clear desk surfaces. We don't move papers or touch computers."),
             ("How often should an office be cleaned?", "Most offices book two to five nights a week, depending on headcount and kitchen use."),
             ("Can you clean during the day?", "We focus on evenings so your team isn't disturbed. Ask about day porter work.")]},
    {"key": "gym", "slug": "gym-cleaning", "name": "Gym and studio cleaning", "kind": "gym",
     "h1": "Gym and studio cleaning in NYC", "title": "Gym & Studio Cleaning NYC & Long Island | Clean by Morning",
     "lead": "Nightly cleaning for gyms, yoga and pilates studios: floors, mats, locker rooms and equipment touch points, done after your last class.",
     "nightly": ["Studio floors cleaned with products safe for your flooring", "Equipment touch points: handles, benches, consoles",
                 "Locker rooms and showers scrubbed and disinfected", "Mirrors and glass", "Front desk and lobby", "Trash out and liners replaced"],
     "clinical": ["We schedule after your last class and finish before your first", "Floor products matched to your surface: wood, rubber or vinyl",
                  "Showers and drains get extra time", "Photos of locker rooms texted after each clean, if you want them"],
     "faq": [("Do you clean the equipment?", "We wipe and disinfect touch points on equipment every visit. Deep equipment cleaning is a separate quote."),
             ("Can you clean every night?", "Yes. Many gyms book five to seven nights a week."),
             ("Do you do showers and locker rooms?", "Yes, every visit, including drains and grout.")]},
    {"key": "postcon", "slug": "post-construction-cleaning", "name": "Post-construction cleaning", "kind": "postcon",
     "h1": "Post-construction cleaning in NYC", "title": "Post-Construction Cleaning NYC & Long Island | Clean by Morning",
     "lead": "A one-time clean after a build-out or renovation, so a new office or practice can open: dust, debris, windows, fixtures and floors.",
     "nightly": ["Construction dust removed from every surface, ledge and vent", "Interior windows, frames and sills", "Fixtures, cabinets and drawers inside and out",
                 "Floors vacuumed, scrubbed and mopped", "Stickers, paint spots and adhesive removed where safe", "Final wipe-down so the space is move-in ready"],
     "clinical": [f"Priced per square foot, from ${postcon_price(1000):,} for small spaces", f"{int(PRICING['deposit'] * 100)}% deposit to book, the rest when the space passes your walkthrough",
                  "We coordinate with your contractor's punch list", "Medical and dental build-outs cleaned to opening standard"],
     "faq": [("When should post-construction cleaning happen?", "After trades finish and before furniture or equipment moves in. A second light clean after move-in is often worth it."),
             ("How is it priced?", f"By square foot, about ${PRICING['postcon_per_sqft']:.2f} per square foot with a ${PRICING['postcon_min']} minimum, confirmed at the walkthrough."),
             ("Do you remove construction debris?", "We remove dust and small debris. Large debris and dumpsters stay with your contractor.")]},
]
SVC = {s["key"]: s for s in SERVICES}

AREAS = [
    {"slug": "brooklyn", "name": "Brooklyn", "h1": "Office cleaning in Brooklyn",
     "hoods": ["Downtown Brooklyn", "Brooklyn Heights", "Park Slope", "Williamsburg", "DUMBO", "Bay Ridge", "Bensonhurst", "Sheepshead Bay"],
     "lead": "Evening cleaning for medical, dental and office spaces across Brooklyn, from Downtown towers to ground-floor practices on the avenues.",
     "body": ["A lot of Brooklyn practices sit on the ground floor of a brownstone or a mixed-use building, with a street entrance and no freight elevator. We carry our own equipment and work around what the building allows.",
              "Downtown Brooklyn and DUMBO have newer office buildings with security desks. We register with the building before the first night, so the guard knows who we are.",
              "We drive to every job, which means we can serve Bay Ridge, Bensonhurst and Sheepshead Bay as easily as the neighborhoods by the bridges."]},
    {"slug": "manhattan", "name": "Manhattan", "h1": "Office cleaning in Manhattan",
     "hoods": ["the Financial District", "Tribeca", "the Flatiron District", "Midtown", "Murray Hill", "the Upper East Side", "the Upper West Side"],
     "lead": "After-hours cleaning for medical practices and small offices in Manhattan, scheduled around building rules and security desks.",
     "body": ["Most Manhattan office buildings require vendors to send a certificate of insurance naming building management before working after hours. We send it before your first night.",
              "Many medical practices on the Upper East Side and in Murray Hill share buildings with other offices, so the clean has to fit the building's service hours. We plan the route around them.",
              "We clean small and mid-size spaces: single-floor practices, studios and offices up to about 15,000 square feet."]},
    {"slug": "nassau-county", "name": "Nassau County", "h1": "Office cleaning in Nassau County",
     "hoods": ["Garden City", "Mineola", "Great Neck", "Manhasset", "Lake Success", "Hicksville", "Rockville Centre", "Massapequa"],
     "lead": "Evening cleaning for medical offices, dental practices and office parks across Nassau County, Long Island.",
     "body": ["Nassau has a large share of medical and dental practices in office parks and medical buildings with their own parking, which makes evening cleaning straightforward.",
              "Practices in Garden City, Mineola, Great Neck and Lake Success often run late appointments. We schedule after the last patient and finish before the morning team.",
              "We're a short drive from the city line, so Nassau accounts get the same checklist and the same nightly photos as our NYC clients."]},
]

FAQ = [
    ("How much does office cleaning cost?", f"We charge by cleaning time: about ${PRICING['hourly']} per hour, with a ${PRICING['min_visit']} minimum per visit. A 2,000 square foot medical office cleaned three nights a week is about ${monthly_price('medical', 2000, 2, 3):,} a month. The estimator shows your number."),
    ("When do you clean?", "After you close, usually between 6 PM and 2 AM. You pick the nights, and we're done before you open."),
    ("Who does the cleaning?", "Clean by Morning is owner-operated. The owner cleans or inspects every account, so you have one person responsible."),
    ("Do you clean medical and dental offices?", "Yes, they're most of what we do. We use color-coded microfiber and EPA-registered disinfectants, and we never handle sharps or regulated medical waste."),
    ("How do I pay?", "Monthly, by ACH autopay on the 1st. The first month is paid before the first clean. One-time jobs take a 50% deposit."),
    ("Is there a long contract?", "No. It's month to month. Either side can end it with 30 days' notice."),
    ("Do you bring supplies?", "Yes. Restroom paper, soap and liners can be restocked at cost, or you can supply your own."),
    ("How do keys and alarms work?", "You give us a key or fob and an alarm code. We store them securely, arm the alarm when we leave, and text you when we're done."),
    ("How fast can you start?", "Usually within a week of the walkthrough."),
]


def proof_lines():
    out = []
    if PROOF["insured"]:
        out.append("General liability insured; certificate available on request")
    if PROOF["bonded"]:
        out.append("Bonded")
    if PROOF["workers_comp"]:
        out.append("Workers' compensation insured")
    if PROOF["review_count"] and PROOF["rating"]:
        out.append(f'{PROOF["rating"]} stars from {PROOF["review_count"]} Google reviews')
    return out


# ---------------------------------------------------------------------------
# Page model: nested clean URLs live, flat files in preview
# ---------------------------------------------------------------------------
def live_path(key):
    if key == "index":
        return "/"
    if key.startswith("svc:"):
        return f"/services/{SVC[key[4:]]['slug']}/"
    if key.startswith("area:"):
        return f"/areas/{key[5:]}/"
    return f"/{key}/"


def live_file(key):
    if key == "404":
        return "404.html"
    p = live_path(key).strip("/")
    return (p + "/index.html") if p else "index.html"


def preview_file(key):
    return "home.html" if key == "index" else key.replace(":", "-").replace("/", "-") + ".html"


class Ctx:
    def __init__(self, preview):
        self.preview = preview

    def href(self, key, anchor=""):
        return (preview_file(key) if self.preview else live_path(key)) + anchor

    def canonical(self, key):
        return B["domain"] + live_path(key)

    def asset(self, name):
        return name if self.preview else "/" + name

    def img(self, key, lazy=True):
        p = PHOTOS[key]
        loading = ' loading="lazy"' if lazy else ""
        return (f'<img src="{self.asset("img/" + p["file"])}" alt="{E(p["alt"])}" '
                f'width="{p["w"]}" height="{p["h"]}"{loading} decoding="async">')


def jsonld(o):
    return f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>'


def business_schema():
    s = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": B["domain"] + "/#business",
         "name": B["name"], "legalName": B["legal_name"], "url": B["domain"] + "/", "telephone": B["phone_e164"], "email": B["email"],
         "description": "Evening commercial cleaning for medical offices, dental practices, offices and gyms in Brooklyn, Manhattan and Nassau County.",
         "areaServed": [{"@type": "City", "name": "Brooklyn, NY"}, {"@type": "City", "name": "Manhattan, NY"}, {"@type": "AdministrativeArea", "name": "Nassau County, NY"}],
         "priceRange": "$$", "openingHours": B["hours_schema"], "image": B["domain"] + "/img/" + PHOTOS["bridge"]["file"], "sameAs": B["same_as"],
         "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}} for s in SERVICES]}
    if PROOF["review_count"] and PROOF["rating"]:
        s["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": PROOF["rating"], "reviewCount": PROOF["review_count"]}
    return s


def crumbs_schema(ctx, trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": ctx.canonical(k)} for i, (k, n) in enumerate(trail)]}


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def crumbs(ctx, label):
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">{E(label)}</li></ol></nav>'


def page_head(ctx, h1, lead, photo, second=None):
    extra = f'<a class="btn btn-line" href="{second[1]}">{E(second[0])}</a>' if second else ""
    return f'''<section class="wrap page-head"><div class="copy reveal"><h1>{E(h1)}</h1><p class="lead">{E(lead)}</p>
<div class="hero-cta" style="justify-content:flex-start"><a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a>{extra}</div></div>
<div class="head-photo tint shutter">{ctx.img(photo, lazy=False)}</div></section>'''


def photo_row(ctx, keys, caption):
    figs = "".join(f'<div class="tint">{ctx.img(k)}</div>' for k in keys)
    return f'<section class="section"><div class="wrap"><figure class="photo-row reveal">{figs}<figcaption class="small">{E(caption)}</figcaption></figure></div></section>'


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
NAV = [("services", "Services"), ("areas", "Areas"), ("pricing", "Pricing")]


def nav_href(ctx, k):
    if k == "services":
        return ctx.href("svc:medical")
    if k == "areas":
        return ctx.href("index", "#areas")
    return ctx.href(k)


def header(ctx, active):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{nav_href(ctx, k)}"{cur if k == active else ""}>{n}</a>' for k, n in NAV)
    menu = "".join(f'<a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a>' for s in SERVICES)
    menu += "".join(f'<a href="{ctx.href("area:" + a["slug"])}">{E(a["name"])}</a>' for a in AREAS)
    menu += f'<a href="{ctx.href("pricing")}">Pricing</a><a href="{ctx.href("faq")}">FAQ</a><a href="{ctx.href("guides")}">Guides</a><a href="{ctx.href("walkthrough")}">Book a walkthrough</a>'
    bar = ""
    if ctx.preview:
        bar = ('<div class="preview-bar"><div class="wrap"><strong>Preview</strong><span>The phone number is a placeholder. The form opens an email until a form service is connected.</span>'
               '<a href="one-pager.html">Capability statement</a><a href="home.html">Home</a></div></div>')
    return f'''{bar}<header class="site-header"><div class="wrap">
<a class="wordmark" href="{ctx.href("index")}">Clean by Morning</a>
<nav class="nav" aria-label="Main">{links}</nav>
<a class="btn btn-paper header-cta" href="{ctx.href("walkthrough")}">Book a walkthrough</a>
<details class="menu"><summary>Menu</summary><nav class="menu-panel" aria-label="Menu">{menu}</nav></details>
</div></header>'''


def footer(ctx):
    svc = " · ".join(f'<a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a>' for s in SERVICES)
    areas = " · ".join(f'<a href="{ctx.href("area:" + a["slug"])}">{E(a["name"])}</a>' for a in AREAS)
    social = " · ".join(f'<a href="{E(u)}">{E(u.split("//")[-1].split("/")[0])}</a>' for u in B["same_as"])
    return f'''<footer class="site-footer"><div class="wrap">
<div class="foot-top"><div class="foot-notes"><strong>Clean by Morning</strong><span>Evening cleaning for medical, dental and office spaces in Brooklyn, Manhattan and Nassau County.</span>
<span>{E(B["cleaning_hours"])}. {E(B["office_hours"])}.</span></div><a href="#main">Back to top</a></div>
<a class="phone-line num" href="tel:{B["phone_e164"]}">{E(B["phone_display"])}</a>
<div class="foot-links"><span>{svc}</span><span>{areas}</span><span><a href="{ctx.href("pricing")}">Pricing</a> · <a href="{ctx.href("faq")}">FAQ</a> · <a href="{ctx.href("guides")}">Guides</a> · <a href="{ctx.href("about")}">About</a> · <a href="{ctx.href("walkthrough")}">Walkthrough</a></span>{f"<span>{social}</span>" if social else ""}</div>
<div class="foot-meta"><span>{E(B["email"])}</span><span>{CREDITS}</span><span>{E(B["city_line"])} · © {B["year"]} {E(B["legal_name"])}</span></div>
</div></footer>'''


def action_bar(ctx):
    return (f'<div class="action-bar"><a class="btn btn-line" href="tel:{B["phone_e164"]}">Call</a>'
            f'<a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a></div>')


def page(ctx, key, title, desc, body, active=None, schema=(), noindex=False, wrapper=True):
    canon = ctx.canonical(key)
    ga = ""
    if B["ga4_id"] and not ctx.preview:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={B["ga4_id"]}"></script>'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{B["ga4_id"]}");</script>')
    cfg = {"pricing": PRICING, "email": B["email"], "phone": B["phone_e164"], "phoneDisplay": B["phone_display"],
           "formEndpoint": B["form_endpoint"], "walkthrough": ctx.href("walkthrough")}
    head = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<script>document.documentElement.classList.add("js");window.CBM={json.dumps(cfg)};</script>
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ""}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:site_name" content="Clean by Morning">
<meta property="og:image" content="{B["domain"]}/img/{PHOTOS["bridge"]["file"]}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0034eb">
<link rel="icon" href="{ctx.asset("favicon.svg")}" type="image/svg+xml">
<link rel="preload" href="{ctx.asset("fonts/sentient-300.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{ctx.asset("styles.css")}">
{ga}{"".join(jsonld(s) for s in schema)}'''
    content = f'''{header(ctx, active)}
<main id="main">
{body}
</main>
{footer(ctx)}
{action_bar(ctx)}
<script src="{ctx.asset("site.js")}" defer></script>'''
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
def estimator(preset="medical"):
    kinds = [("medical", "Medical"), ("dental", "Dental"), ("office", "Office"), ("gym", "Gym or studio"), ("postcon", "Post-construction, one time")]
    chips = "".join(f'<label class="chip"><input type="radio" name="kind" value="{k}"{" checked" if k == preset else ""}><span>{n}</span></label>' for k, n in kinds)
    nights = "".join(f'<label class="chip"><input type="radio" name="nights" value="{n}"{" checked" if n == 3 else ""}><span>{n}</span></label>' for n in range(1, 8))
    rest = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n}</option>' for n in range(0, 9))
    if preset == "postcon":
        figure, detail = postcon_price(2000), "One-time clean, 2,000 sq ft."
    else:
        figure, detail = monthly_price(preset, 2000, 2, 3), f"About ${visit_price(preset, 2000, 2)} a visit, 3 nights a week."
    return f'''<form class="estimator" data-ui data-estimator novalidate aria-label="Cleaning price estimator">
<div class="est-fields">
<h3>Estimate your price</h3>
<fieldset class="field"><legend>Type of space</legend><div class="chips">{chips}</div></fieldset>
<div class="field"><label for="e-sqft">Square feet: <span data-sqft-out class="num">2,000</span></label><input id="e-sqft" name="sqft" type="range" min="500" max="15000" step="250" value="2000"></div>
<fieldset class="field" data-recurring><legend>Nights a week</legend><div class="chips">{nights}</div></fieldset>
<div class="field" data-recurring><label for="e-rest">Restrooms</label><select id="e-rest" name="restrooms">{rest}</select></div>
</div>
<div class="est-result" aria-live="polite">
<p class="small" data-est-label>{"One-time price" if preset == "postcon" else "Estimated monthly price"}</p>
<p class="est-figure" data-est-figure>${figure:,}</p>
<p data-est-detail>{detail}</p>
<p class="small">An estimate before tax. We confirm the price after a 15-minute walkthrough.</p>
<a class="btn btn-accent" data-est-cta href="#">Book a walkthrough</a>
</div>
</form>'''


def faq_table(items, heading="Questions"):
    rows = "".join(f'<div class="faq-row reveal"><h3 class="q">{E(q)}</h3><p class="a">{E(a)}</p></div>' for q, a in items)
    return f'''<section class="section" id="faq"><div class="wrap faq-table">
<div class="faq-row head"><h2 class="q">{E(heading)}</h2><span></span></div>{rows}</div></section>'''


def contact_field(ctx):
    user, dom = B["email"].split("@")
    return f'''<section class="contact-field" id="contact"><div class="wrap">
<p class="ask">Send us your square footage and how many nights a week. We'll reply with a price the same day.</p>
<a class="mail-line" href="mailto:{B["email"]}?subject=Cleaning%20quote">{E(user)}@<wbr>{E(dom)}</a>
<div class="contact-corners"><span><a href="tel:{B["phone_e164"]}" class="num">{E(B["phone_display"])}</a> · {E(B["city_line"])}</span>
<span><a href="{ctx.href("walkthrough")}">Book a walkthrough</a> · <a href="{ctx.href("one-pager")}">Capability statement</a></span></div>
</div></section>'''


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def home(ctx, wrapper=True):
    hoods = [f'<a href="{ctx.href("area:" + a["slug"])}">{E(h)}</a>' for a in AREAS for h in a["hoods"][:3]]
    names = ", ".join(hoods[:-1]) + " and " + hoods[-1]
    proof = proof_lines()
    clients = f' Clients include {E(", ".join(PROOF["clients"]))}.' if PROOF["clients"] else ""
    proof_html = f'<ul class="list">{"".join(f"<li>{E(x)}</li>" for x in proof)}</ul>' if proof else ""
    body = f'''<section class="hero">
<div class="hero-media tint shutter">{ctx.img("bridge", lazy=False)}</div>
<div class="wrap hero-inner">
<h1>Medical offices, clean by morning</h1>
<p class="horizon"><span class="h-left">Evening cleaning for medical, dental and office spaces</span><span class="h-right">in Brooklyn, Manhattan and Nassau County.</span></p>
<div class="hero-cta"><a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a><a class="btn btn-line" href="#pricing">See prices</a></div>
</div></section>

<section class="section" id="what"><div class="wrap reveal">
<h2 class="visually-hidden">What we do</h2>
<p class="picture-para">We arrive after your last patient leaves <span class="slot" aria-hidden="true">{ctx.img("windows")}</span>, disinfect every exam room and restroom, and lock up by midnight <span class="slot" aria-hidden="true">{ctx.img("rain")}</span>. You get photos before you open.</p>
<div class="after-para"><p>One owner-operated crew, one written checklist, month-to-month contracts.{clients}</p>{proof_html}
<a class="btn btn-accent" href="{ctx.href("svc:medical")}">What a medical clean includes</a></div>
</div></section>

<section class="verbs" aria-label="How it works">
<div class="panel">{ctx.img("rain")}<div class="verb-track"><p class="verb">Lock up</p></div><p class="panel-note">You close at 6 and leave. We have the key, the alarm code and the checklist.</p></div>
<div class="panel">{ctx.img("windows")}<div class="verb-track"><p class="verb">We clean</p></div><p class="panel-note">Exam rooms, restrooms, floors and trash, the same way every night. Photos when we finish.</p></div>
<div class="panel">{ctx.img("morning")}<div class="verb-track"><p class="verb">Open up</p></div><p class="panel-note">Your team walks into a clean office. Billing is one monthly autopay, nothing to chase.</p></div>
</section>

<section class="price-section" id="pricing"><div class="wrap">
<h2 class="price-sentence">From <span class="price-block num">${PRICING["min_visit"]}</span> a night</h2>
<div class="price-row"><p>About ${PRICING["hourly"]} per cleaning hour, with supplies included. Monthly autopay, month to month, 30 days' notice to cancel.</p>
<a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a></div>
{estimator()}
</div></section>

<section class="wrap" id="areas" aria-label="Where we clean"><p class="names reveal" data-names><span class="lead-in">We clean in</span> {names}.</p></section>

{faq_table(FAQ[:6])}
{contact_field(ctx)}'''
    return page(ctx, "index", "Medical & Office Cleaning NYC and Long Island | Clean by Morning",
                f"Evening cleaning for medical, dental and office spaces in Brooklyn, Manhattan and Nassau County. From ${PRICING['min_visit']} a visit, month to month. Book a walkthrough.",
                body, schema=[business_schema(), faq_schema(FAQ[:6])], wrapper=wrapper)


def service_page(ctx, s):
    trail = [("index", "Home"), ("svc:" + s["key"], s["name"])]
    nightly = "".join(f"<li>{E(x)}</li>" for x in s["nightly"])
    clinical = "".join(f"<li>{E(x)}</li>" for x in s["clinical"])
    areas = "".join(f'<li><a href="{ctx.href("area:" + a["slug"])}">{E(s["name"])} in {E(a["name"])}</a></li>' for a in AREAS)
    others = "".join(f'<li><a href="{ctx.href("svc:" + o["key"])}">{E(o["name"])}</a></li>' for o in SERVICES if o is not s)
    if s["kind"] == "postcon":
        start = postcon_price(1000)
        price_line = f'From <span class="price-block num">${start}</span>, one time'
        price_note = f"About ${PRICING['postcon_per_sqft']:.2f} per square foot, {int(PRICING['deposit'] * 100)}% deposit to book, the rest on completion."
    else:
        start = PRICING["min_visit"]
        price_line = f'From <span class="price-block num">${start}</span> a night'
        price_note = f"About ${PRICING['hourly']} per cleaning hour, supplies included, billed monthly by autopay."
    schema = {"@context": "https://schema.org", "@type": "Service", "name": s["h1"], "serviceType": s["name"], "provider": {"@id": B["domain"] + "/#business"},
              "areaServed": ["Brooklyn, NY", "Manhattan, NY", "Nassau County, NY"],
              "offers": {"@type": "Offer", "priceCurrency": "USD", "price": str(start)}, "url": ctx.canonical("svc:" + s["key"])}
    photo = {"medical": "windows", "dental": "morning", "office": "bridge", "gym": "rain", "postcon": "morning"}[s["key"]]
    body = f'''{crumbs(ctx, s["name"])}
{page_head(ctx, s["h1"], s["lead"], photo, ("Estimate the price", "#estimate"))}
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>Every visit</h2></div><div class="right5"><ul class="list">{nightly}</ul></div></div></section>
{photo_row(ctx, [k for k in ("bridge", "rain", "windows", "morning") if k != photo], "After hours in New York: we start when you lock up.")}
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>How we work</h2></div><div class="right5"><ul class="list">{clinical}</ul></div></div></section>
<section class="price-section" id="estimate" style="margin-top:clamp(120px,14vw,220px)"><div class="wrap">
<h2 class="price-sentence">{price_line}</h2>
<div class="price-row"><p>{price_note}</p><a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a></div>
{estimator(s["kind"])}</div></section>
{faq_table(s["faq"], "Questions about " + s["name"].lower())}
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>Where we do it</h2></div><div class="right5 stack"><ul class="link-row">{areas}</ul><ul class="link-row">{others}</ul></div></div></section>
{contact_field(ctx)}'''
    return page(ctx, "svc:" + s["key"], s["title"], s["lead"][:155], body, active="services",
                schema=[schema, crumbs_schema(ctx, trail), faq_schema(s["faq"])])


def area_page(ctx, a):
    trail = [("index", "Home"), ("area:" + a["slug"], a["name"])]
    paras = "".join(f"<p>{E(p)}</p>" for p in a["body"])
    svc = "".join(f'<li><a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a></li>' for s in SERVICES)
    hoods = ", ".join(a["hoods"][:-1]) + " and " + a["hoods"][-1]
    others = "".join(f'<li><a href="{ctx.href("area:" + o["slug"])}">{E(o["name"])}</a></li>' for o in AREAS if o is not a)
    schema = business_schema() | {"areaServed": {"@type": "Place", "name": a["name"] + ", NY"}}
    photo = "morning" if a["slug"] == "nassau-county" else ("bridge" if a["slug"] == "brooklyn" else "windows")
    body = f'''{crumbs(ctx, a["name"])}
{page_head(ctx, a["h1"], a["lead"], photo, ("See prices", ctx.href("pricing")))}
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>Cleaning in {E(a["name"])}</h2></div><div class="right5 stack">{paras}</div></div></section>
<section class="wrap" aria-label="Neighborhoods"><p class="names reveal"><span class="lead-in">In {E(a["name"])} we clean in</span> {E(hoods)}.</p></section>
<section class="section" style="padding-top:0"><div class="wrap grid reveal"><div class="left6"><h2>Services in {E(a["name"])}</h2></div><div class="right5 stack"><ul class="link-row">{svc}</ul><p>We also serve</p><ul class="link-row">{others}</ul></div></div></section>
{photo_row(ctx, [k for k in ("bridge", "rain", "windows", "morning") if k != photo], "Evenings in New York, when we work.")}
{contact_field(ctx)}'''
    return page(ctx, "area:" + a["slug"], f'Office & Medical Cleaning {a["name"]}, NY | Clean by Morning', a["lead"][:155], body, active="areas",
                schema=[schema, crumbs_schema(ctx, trail)])


def pricing_page(ctx):
    trail = [("index", "Home"), ("pricing", "Pricing")]
    sizes = [1000, 2000, 3500, 5000, 8000]
    rows = []
    for k, n in [("medical", "Medical, 3 nights a week"), ("dental", "Dental, 3 nights a week"), ("office", "Office, 3 nights a week"), ("gym", "Gym or studio, 5 nights a week")]:
        nights = 5 if k == "gym" else 3
        cells = "".join(f'<td class="n">${monthly_price(k, sz, 1 if sz < 2000 else 2 if sz < 5000 else 4, nights):,}</td>' for sz in sizes)
        rows.append(f'<tr><th scope="row">{n}</th>{cells}</tr>')
    rows.append('<tr><th scope="row">Post-construction, one time</th>' + "".join(f'<td class="n">${postcon_price(sz):,}</td>' for sz in sizes) + "</tr>")
    head = "".join(f"<th>{sz:,} sq ft</th>" for sz in sizes)
    body = f'''{crumbs(ctx, "Pricing")}
{page_head(ctx, "Office cleaning prices", "Monthly prices for evening cleaning in Brooklyn, Manhattan and Nassau County, before tax. Billed once a month by autopay.", "rain", ("Estimate yours", "#estimate"))}
<section class="section"><div class="wrap stack reveal"><h2>Prices by size</h2>
<div class="table-scroll"><table class="price-table"><thead><tr><th>Space and schedule</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="note">Monthly figures assume {PRICING["weeks_per_month"]} weeks a month and 1–4 restrooms by size. New York sales tax applies to commercial cleaning. Your exact price comes after a 15-minute walkthrough.</p>
</div></section>
{photo_row(ctx, ["bridge", "windows", "morning"], "Priced by the hour of cleaning, not by guesswork.")}
<section class="price-section" id="estimate" style="margin-top:clamp(120px,14vw,220px)"><div class="wrap">
<h2 class="price-sentence">Your price, in a minute</h2>{estimator()}</div></section>
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>How billing works</h2></div><div class="right5"><ul class="list">
<li>One monthly price, billed on the 1st by ACH autopay</li><li>First month paid before the first clean</li><li>Month to month; 30 days' notice to cancel</li>
<li>One-time jobs: {int(PRICING["deposit"] * 100)}% deposit to book, the rest on completion</li><li>Restroom paper, soap and liners restocked at cost if you want</li></ul></div></div></section>
{contact_field(ctx)}'''
    return page(ctx, "pricing", "Office Cleaning Prices NYC & Long Island | Clean by Morning",
                f"Monthly prices for medical, dental, office and gym cleaning in Brooklyn, Manhattan and Nassau County. From ${PRICING['min_visit']} a visit.",
                body, active="pricing", schema=[crumbs_schema(ctx, trail)])


def walkthrough_page(ctx):
    trail = [("index", "Home"), ("walkthrough", "Book a walkthrough")]
    opts = "".join(f"<option>{E(s['name'])}</option>" for s in SERVICES)
    body = f'''{crumbs(ctx, "Book a walkthrough")}
<section class="section" style="padding-top:clamp(48px,6vw,96px)"><div class="wrap grid">
<div class="left6 stack reveal"><h1 style="font-size:var(--step-head)">Book a 15-minute walkthrough</h1><p class="statement">We look at the space, agree on the checklist and send a fixed monthly price the same day.</p>
<ul class="list"><li>Free, with no obligation</li><li>Before or after your hours, whichever suits you</li><li>Price in writing within 24 hours</li><li>Most clients start within a week</li></ul>
<p>Rather talk? Call <a href="tel:{B["phone_e164"]}" class="num">{E(B["phone_display"])}</a>.</p></div>
<form class="form right5" data-walkthrough novalidate aria-label="Walkthrough request">
<div class="field"><label for="w-name">Your name</label><input id="w-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="w-company">Practice or company</label><input id="w-company" name="company" type="text" autocomplete="organization"></div>
<div class="field"><label for="w-email">Email</label><input id="w-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="w-phone">Phone</label><input id="w-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field"><label for="w-type">Type of space</label><select id="w-type" name="type">{opts}</select></div>
<div class="field"><label for="w-address">Address or neighborhood</label><input id="w-address" name="address" type="text" autocomplete="street-address"></div>
<div class="field"><label for="w-sqft">Approximate square feet</label><input id="w-sqft" name="sqft" type="text" inputmode="numeric"></div>
<div class="field"><label for="w-notes">Nights a week, and anything else</label><textarea id="w-notes" name="notes"></textarea></div>
<button class="btn" type="submit">Request a walkthrough</button><p class="form-msg" data-form-msg role="status"></p>
</form></div></section>'''
    return page(ctx, "walkthrough", "Book a Cleaning Walkthrough | Clean by Morning",
                "Book a free 15-minute walkthrough for medical, dental or office cleaning in Brooklyn, Manhattan or Nassau County. Price in writing within 24 hours.",
                body, schema=[crumbs_schema(ctx, trail)])


def faq_page(ctx):
    trail = [("index", "Home"), ("faq", "FAQ")]
    body = f'''{crumbs(ctx, "FAQ")}
{page_head(ctx, "Commercial cleaning questions", "Prices, schedules, keys and alarms, payment and contracts: the questions office managers ask before they sign.", "morning")}
{faq_table(FAQ, "Questions")}
{photo_row(ctx, ["bridge", "rain", "windows"], "After hours in New York, when we work.")}
{contact_field(ctx)}'''
    return page(ctx, "faq", "Commercial Cleaning FAQ | Clean by Morning",
                "Answers about Clean by Morning's evening office and medical cleaning: prices, schedules, keys and alarms, payment and contracts.",
                body, schema=[faq_schema(FAQ), crumbs_schema(ctx, trail)])


def about_page(ctx):
    trail = [("index", "Home"), ("about", "About")]
    body = f'''{crumbs(ctx, "About")}
{page_head(ctx, "One crew, one checklist", "Clean by Morning is an owner-operated cleaning company for medical practices and small offices in New York City and Nassau County.", "windows")}
{photo_row(ctx, ["bridge", "rain", "morning"], "From lock-up to opening: the hours we work.")}
<section class="section"><div class="wrap grid reveal"><div class="left6"><h2>Why we work this way</h2></div><div class="right5 stack">
<p>Office managers tell us the same story: a different cleaner every month, a checklist nobody follows, and an invoice that keeps changing. We built Clean by Morning to fix that.</p>
<p>The owner cleans or inspects every account. Every visit follows the same written checklist. Prices are fixed and billed once a month, and you can leave with 30 days' notice.</p>
<p>We clean in the evening, after you close, so your patients and staff never see us, only the result.</p></div></div></section>
{contact_field(ctx)}'''
    return page(ctx, "about", "About Clean by Morning | NYC Office Cleaning",
                "Clean by Morning is an owner-operated evening cleaning company for medical practices and small offices in NYC and Nassau County.",
                body, schema=[crumbs_schema(ctx, trail)])


def one_pager(ctx):
    proof = proof_lines() or ["Certificate of insurance sent on request once coverage is in place"]
    sub = 'style="font-size:var(--step-statement)"'
    body = f'''<section class="section" style="padding-top:48px"><div class="wrap stack">
<h1 style="font-size:var(--step-head)">Capability statement</h1>
<div class="grid"><div class="left6 stack">
<p class="statement">{E(B["legal_name"])}: evening commercial cleaning for medical offices, dental practices, offices and gyms in Brooklyn, Manhattan and Nassau County.</p>
<h2 {sub}>Services</h2><ul class="list">{"".join(f"<li>{E(s['name'])}</li>" for s in SERVICES)}</ul>
<h2 {sub}>How we work</h2><ul class="list"><li>Owner-operated; the owner cleans or inspects every account</li><li>Written checklist per site; photos after each visit on request</li>
<li>Color-coded microfiber and EPA-registered disinfectants</li><li>No handling of sharps or regulated medical waste</li><li>Keys and alarm codes stored securely</li></ul></div>
<div class="right5 stack"><h2 {sub}>Commercial terms</h2><ul class="list"><li>Fixed monthly price, ACH autopay on the 1st</li><li>Month to month, 30 days' notice</li>
<li>From ${PRICING["min_visit"]} per visit; about ${PRICING["hourly"]} per cleaning hour</li><li>NAICS 561720, Janitorial Services</li>{"".join(f"<li>{E(x)}</li>" for x in proof)}</ul>
<h2 {sub}>Contact</h2><p>{E(B["email"])}<br><span class="num">{E(B["phone_display"])}</span><br>{E(B["domain"].replace("https://", ""))}</p></div></div>
</div></section>'''
    return page(ctx, "one-pager", "Clean by Morning Capability Statement", "Capability statement for Clean by Morning Office Cleaning.", body, noindex=True)


GUIDES = [
    {"slug": "office-cleaning-cost-nyc", "title": "How much does office cleaning cost in NYC?",
     "meta": "What office and medical cleaning costs in Brooklyn, Manhattan and Nassau County, what changes the price, and worked examples by size.",
     "lead": "Most commercial cleaning in New York is priced by the hours it takes, multiplied by how many nights a week you need it. Here's how that works, with our own prices as examples.",
     "sections": [
         ("What sets the price", ["Square footage: a routine office cleans at roughly 2,000–3,000 square feet an hour; medical and dental spaces take longer because every room is disinfected.",
                                  "Nights a week: most offices book two to five; gyms often book five to seven.",
                                  "Restrooms: each one adds time every visit.",
                                  "Building rules: Manhattan buildings often limit service hours and require a certificate of insurance, which can affect scheduling."]),
         ("Worked examples (Clean by Morning prices)", [f"1,000 sq ft office, 3 nights a week: about ${monthly_price('office', 1000, 1, 3):,} a month",
                                                       f"2,000 sq ft medical office, 3 nights a week: about ${monthly_price('medical', 2000, 2, 3):,} a month",
                                                       f"3,500 sq ft dental office, 5 nights a week: about ${monthly_price('dental', 3500, 2, 5):,} a month",
                                                       f"5,000 sq ft office, 3 nights a week: about ${monthly_price('office', 5000, 4, 3):,} a month"]),
         ("Sales tax", ["Commercial cleaning is generally subject to New York sales tax. The rate depends on where the work is done: 8.875% in New York City and 8.625% in Nassau County. Ask any cleaner whether their quote includes it."]),
         ("Questions to ask any cleaning company", ["Is the price fixed monthly, or does it change with hours?", "Is there a contract term, and how much notice do I need to cancel?",
                                                   "Can you send a certificate of insurance before you start?", "Who will clean my office, and will it be the same person each night?"]),
     ]},
    {"slug": "medical-office-cleaning-checklist", "title": "Medical office cleaning checklist",
     "meta": "A nightly, weekly and monthly cleaning checklist for medical practices, and what a cleaning company should never handle.",
     "lead": "A written checklist is what makes a medical office clean the same way every night. This is the list we work from, which you can adapt for your own practice.",
     "sections": [
         ("Every night", ["Exam rooms: counters, chairs, exam table surfaces outside the paper, door handles and light switches disinfected",
                          "Waiting room: chairs, front desk, pens, clipboards and door handles", "Restrooms: toilets, sinks, mirrors, dispensers; paper and soap restocked",
                          "Trash and recycling emptied; liners replaced", "Hard floors damp-mopped, carpets vacuumed"]),
         ("Every week", ["Baseboards and vents dusted", "Inside microwaves and break-room fridge fronts", "Chair legs and bases wiped", "Glass partitions and entry doors"]),
         ("Every month", ["High dusting: light fixtures, tops of cabinets", "Upholstered waiting-room chairs vacuumed", "Floor machine scrub or carpet spot treatment as needed"]),
         ("How it should be done", ["Color-coded microfiber, so restroom cloths never touch exam rooms", "EPA-registered disinfectants, left wet for the contact time on the label",
                                    "Work from clean areas to dirty areas, and high surfaces to low"]),
         ("What a cleaner should never handle", ["Sharps containers and regulated medical waste: these go with your licensed medical waste hauler",
                                                 "Patient files, screens and anything in drawers"]),
     ]},
    {"slug": "dental-office-cleaning-frequency", "title": "How often should a dental office be cleaned?",
     "meta": "How many nights a week dental practices usually book cleaning, what gets cleaned each visit, and what stays with the clinical team.",
     "lead": "Most dental practices book cleaning three to five nights a week. The right number depends on patient volume and how many operatories you run.",
     "sections": [
         ("A rule of thumb", ["Open four or five days with full schedules: clean every night you're open", "Open three days or fewer: clean the nights after you see patients",
                              "Restrooms and reception: every visit, whatever the schedule"]),
         ("What the cleaning crew does", ["Operatory floors, counters outside the clinical zone, door handles and switches", "Sterilization-area floors and sinks",
                                          "Reception, restrooms, break room and trash"]),
         ("What stays with your clinical team", ["Chairside surfaces and equipment between patients", "Sharps, amalgam and regulated waste, through your licensed hauler"]),
         ("Pricing it", [f"A 2,000 sq ft practice cleaned four nights a week is about ${monthly_price('dental', 2000, 2, 4):,} a month at our rates.",
                         "The estimator on our pricing page shows other sizes and schedules."]),
     ]},
]


def guide_page(ctx, g):
    key = "guides/" + g["slug"]
    trail = [("index", "Home"), ("guides", "Guides"), (key, g["title"])]
    secs = "".join(f'<h2>{E(h)}</h2><ul>{"".join(f"<li>{E(x)}</li>" for x in items)}</ul>' for h, items in g["sections"])
    schema = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["meta"],
              "author": {"@type": "Organization", "name": B["name"]}, "publisher": {"@id": B["domain"] + "/#business"},
              "mainEntityOfPage": ctx.canonical(key), "image": B["domain"] + "/img/" + PHOTOS["windows"]["file"]}
    body = f'''{crumbs(ctx, "Guides")}
{page_head(ctx, g["title"], g["lead"], "windows", ("See prices", ctx.href("pricing")))}
<section class="section"><div class="wrap"><article class="article reveal">{secs}
<p>Want this checklist for your own office, priced? <a class="text-link" href="{ctx.href("walkthrough")}">Book a 15-minute walkthrough</a>.</p></article></div></section>
{photo_row(ctx, ["bridge", "rain", "morning"], "After hours in New York, when we work.")}
{contact_field(ctx)}'''
    return page(ctx, key, f'{g["title"]} | Clean by Morning', g["meta"], body, schema=[schema, crumbs_schema(ctx, trail)])


def guides_index(ctx):
    trail = [("index", "Home"), ("guides", "Guides")]
    items = "".join(f'<li><a href="{ctx.href("guides/" + g["slug"])}">{E(g["title"])}</a><p>{E(g["meta"])}</p></li>' for g in GUIDES)
    body = f'''{crumbs(ctx, "Guides")}
{page_head(ctx, "Guides for office managers", "Plain answers about commercial cleaning in New York: what it costs, what it should include, and how often you need it.", "morning")}
<section class="section"><div class="wrap"><ul class="guide-list reveal">{items}</ul></div></section>
{photo_row(ctx, ["bridge", "rain", "windows"], "After hours in New York, when we work.")}
{contact_field(ctx)}'''
    return page(ctx, "guides", "Commercial Cleaning Guides | Clean by Morning",
                "Guides for NYC and Long Island office managers: cleaning costs, medical office checklists and how often to clean a dental office.",
                body, schema=[crumbs_schema(ctx, trail)])


def not_found(ctx):
    body = f'''<section class="wrap page-head"><h1>Page not found</h1><p class="statement">That page doesn't exist.</p>
<div class="hero-cta" style="justify-content:flex-start"><a class="btn btn-accent" href="{ctx.href("walkthrough")}">Book a walkthrough</a></div></section>'''
    return page(ctx, "404", "Page not found | Clean by Morning", "Page not found.", body, noindex=True)


FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#0034eb"/><rect x="14" y="40" width="36" height="10" fill="#e9e34a"/></svg>\n'


def all_pages(ctx):
    pages = {"index": home(ctx), "pricing": pricing_page(ctx), "walkthrough": walkthrough_page(ctx), "faq": faq_page(ctx),
             "about": about_page(ctx), "one-pager": one_pager(ctx), "guides": guides_index(ctx), "404": not_found(ctx)}
    for g in GUIDES:
        pages["guides/" + g["slug"]] = guide_page(ctx, g)
    for s in SERVICES:
        pages["svc:" + s["key"]] = service_page(ctx, s)
    for a in AREAS:
        pages["area:" + a["slug"]] = area_page(ctx, a)
    return pages


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def copy_static(dest):
    for f in ("styles.css", "site.js"):
        shutil.copy(ROOT / "static" / f, dest / f)
    shutil.copytree(ROOT / "static" / "img", dest / "img", dirs_exist_ok=True)
    shutil.copytree(ROOT / "static" / "fonts", dest / "fonts", dirs_exist_ok=True)
    write(dest / "favicon.svg", FAVICON)


def build():
    out = ROOT / "public"
    shutil.rmtree(out, ignore_errors=True)
    ctx = Ctx(False)
    pages = all_pages(ctx)
    for k, t in pages.items():
        write(out / live_file(k), t)
    urls = "".join(f"<url><loc>{ctx.canonical(k)}</loc></url>" for k in pages if k not in ("404", "one-pager"))
    write(out / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write(out / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {B['domain']}/sitemap.xml\n")
    copy_static(out)

    prev = ROOT / "preview"
    shutil.rmtree(prev, ignore_errors=True)
    pctx = Ctx(True)
    pp = all_pages(pctx)
    for k, t in pp.items():
        write(prev / preview_file(k), t)
    entry = home(pctx, wrapper=False).replace("<title>Medical &amp; Office Cleaning NYC and Long Island | Clean by Morning</title>", "<title>Clean by Morning Website</title>", 1)
    write(prev / "index.html", entry)
    copy_static(prev)
    print(f"Built {len(pages)} live pages, {len(pp) + 1} preview pages.")


if __name__ == "__main__":
    build()
