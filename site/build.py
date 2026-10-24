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
    "phone_display": "(516) 518-1731",      # the Quo business line
    "phone_e164": "+15165181731",
    "email": "hello@cleanbymorning.com",    # set up this mailbox on the domain
    "city_line": "New York, NY",
    "office_hours": "Quotes Mon–Sat, 9 AM–7 PM",
    "cleaning_hours": "We clean after you close, 6 PM–2 AM",
    "hours_schema": ["Mo-Sa 09:00-19:00"],
    "form_endpoint": "",    # e.g. a Formspree or Basin URL; empty = the form opens a pre-filled email instead
    "ga4_id": "",           # Google Analytics 4 id, e.g. "G-XXXXXXX"
    "year": 2026,
    "same_as": [],          # Google Business Profile, LinkedIn, Instagram once they exist
    # The owner, shown on the About page. Prospects from cold email look for a real person. Leave empty to hide.
    "owner_name": "",       # e.g. "Mike Rivera"
    "owner_photo": "",      # a file in site/static/img, e.g. "owner.webp" (a real photo of you, 800x1000)
    "owner_bio": "",        # 2-3 sentences in your own words: where you're from, why you started, what you check every night
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
    "lamp": {"file": "street-lamp-in-snow-at-night.webp", "w": 1600, "h": 1000, "alt": "A street lamp glowing in falling snow late at night"},
}
CREDITS = "Photos: Oleg Chursin, Vladimir Kudinov, Charles Forerunner, Riley Briggs and Hide Obara, via Unsplash."

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
    ("Do you clean medical and dental offices?", "Yes, they're our focus. We use color-coded microfiber and EPA-registered disinfectants, and we never handle sharps or regulated medical waste."),
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
        loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
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
         "logo": B["domain"] + "/icon-512.png",
         "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}} for s in SERVICES]}
    if B["owner_name"]:
        s["founder"] = {"@type": "Person", "name": B["owner_name"], "jobTitle": "Owner"}
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
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{ctx.href("index")}">Home</a></li><li aria-current="page">{E(label)}</li></ol></nav>'


# ---------------------------------------------------------------------------
# Design: every page is one night. It opens at dusk in cobalt, darkens through the clean
# and brightens to morning. Section grounds are flat steps (g-dusk → g-s6 → g-dawn → g-day),
# never gradients. Yellow is the horizon bar from the logo and the main button.
# ---------------------------------------------------------------------------
MARK = ('<svg class="mark" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" fill="currentColor"/>'
        '<rect x="14" y="40" width="36" height="10" fill="#e9e34a"/></svg>')

SHORT = {
    "medical": "Exam rooms, waiting room and restrooms, disinfected every visit.",
    "dental": "Operatory floors, sterilization area, reception and restrooms.",
    "office": "Desks, kitchens, restrooms and floors, before your team arrives.",
    "gym": "Studio floors, locker rooms, showers and equipment touch points.",
    "postcon": "A one-time clean after a build-out, so you can open.",
}

# A typical night: (time, period, heading, text, photo, ground)
NIGHT = [
    ("6:00", "PM", "You lock up", "Leave when your last patient does. We already have the key, the alarm code and your checklist.", "rain", "g-dusk"),
    ("6:30", "PM", "We let ourselves in", "Usually the same person every night, through the entrance your building assigns. Alarm off, lights on.", None, "g-s1"),
    ("7:00", "PM", "Exam rooms and operatories", "Counters, chairs, door handles and switches disinfected, with EPA-registered products left wet for their full contact time.", None, "g-s2"),
    ("8:15", "PM", "Restrooms", "Scrubbed with their own color-coded cloths, disinfected, and restocked with paper and soap.", None, "g-s3"),
    ("9:00", "PM", "Floors and trash", "Carpets vacuumed, hard floors damp-mopped with a clean head for each area, trash and recycling out.", None, "g-s4"),
    ("9:45", "PM", "Lights off, alarm on", "We photograph every room, set the alarm and lock the door behind us.", "lamp", "g-s5"),
    ("3:00", "AM", "The office sits clean", "Nothing moves until morning.", "bridge", "g-s6"),
    ("6:30", "AM", "Photos in your inbox", "Pictures of every room, sent when we finished, waiting when you wake up.", None, "g-dawn"),
    ("7:45", "AM", "You open", "Your team walks into a clean office. Billing is one monthly autopay, with nothing to chase.", "morning", "g-day"),
]


def fig(ctx, key, cls="", lazy=True, tint=True):
    t = " tint" if tint else ""
    return f'<figure class="ph{t} {cls}">{ctx.img(key, lazy=lazy)}</figure>'


def ctas(ctx, second=None, on_light=False):
    first = "btn-cobalt" if on_light else "btn-sun"
    extra = f'<a class="btn btn-ghost" href="{second[1]}">{E(second[0])}</a>' if second else ""
    return f'<div class="ctas"><a class="btn {first}" href="{ctx.href("walkthrough")}">Book a walkthrough</a>{extra}</div>'


def page_head(ctx, label, h1, lead, photo, second=None):
    return f'''<section class="g g-dusk head"><div class="wrap head-grid">
<div class="head-copy">{crumbs(ctx, label)}<h1>{E(h1)}</h1><span class="horizon" aria-hidden="true"></span><p class="lead">{E(lead)}</p>{ctas(ctx, second)}</div>
{fig(ctx, photo, "head-photo shutter", lazy=False)}</div></section>'''


def sec_head(h2, lead=""):
    p = f'<p class="lead">{E(lead)}</p>' if lead else ""
    return f'<div class="sec-head"><h2>{E(h2)}</h2>{p}</div>'


def night_sheet(ctx):
    rows = []
    for t, ap, h, txt, photo, g in NIGHT:
        ph = fig(ctx, photo, "row-photo", tint=(g != "g-day")) if photo else ""
        rows.append(f'''<li class="g {g} row"><div class="wrap row-grid reveal"><p class="time num">{t}<span>{ap}</span></p>
<div class="row-copy"><h3>{E(h)}</h3><p>{E(txt)}</p></div>{ph}</div></li>''')
    return f'''<section class="sheet" aria-labelledby="night-h">
<div class="g g-dusk sheet-intro"><div class="wrap">{sec_head("One night at your office", "A typical evening at a 2,000 square foot practice, cleaned three nights a week.").replace("<h2>", '<h2 id="night-h">', 1)}</div></div>
<ol class="rows">{"".join(rows)}</ol></section>'''


def services_list(ctx, heading="What we clean", lead="Five kinds of space. Each gets its own written checklist.", exclude=None):
    items = []
    for s in SERVICES:
        if s is exclude:
            continue
        price = f"from ${postcon_price(1000)}" if s["kind"] == "postcon" else f"from ${PRICING['min_visit']} a visit"
        items.append(f'<li><a href="{ctx.href("svc:" + s["key"])}"><span class="svc-name">{E(s["name"])}</span>'
                     f'<span class="svc-line">{E(SHORT[s["key"]])}</span><span class="svc-price num">{price}</span></a></li>')
    return f'<section class="g g-day section" id="services"><div class="wrap">{sec_head(heading, lead)}<ul class="svc-list reveal">{"".join(items)}</ul></div></section>'


def price_band(ctx, heading_html, note, preset="medical", anchor="pricing"):
    return f'''<section class="g g-dawn section" id="{anchor}"><div class="wrap price-grid">
<div class="price-copy"><h2>{heading_html}</h2><p>{E(note)}</p>{ctas(ctx, ("Full price list", ctx.href("pricing")), on_light=True)}</div>
{estimator(preset)}</div></section>'''


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
<p class="est-figure num" data-est-figure>${figure:,}</p>
<p data-est-detail>{detail}</p>
<p class="small">An estimate before tax. We confirm the price after a 15-minute walkthrough.</p>
<a class="btn btn-sun" data-est-cta href="#">Book a walkthrough</a>
</div>
</form>'''


def areas_band(ctx, heading="Where we clean"):
    photos = {"brooklyn": "bridge", "manhattan": "windows", "nassau-county": "morning"}
    cols = "".join(f'''<div class="area reveal">{fig(ctx, photos[a["slug"]])}<h3><a href="{ctx.href("area:" + a["slug"])}">{E(a["name"])}</a></h3>
<p>{E(", ".join(a["hoods"][:5]))} and more.</p></div>''' for a in AREAS)
    return f'<section class="g g-night section" id="areas"><div class="wrap">{sec_head(heading, "We drive to every job, so the outer neighborhoods cost the same as the ones by the bridges.")}<div class="area-cols">{cols}</div></div></section>'


def faq_table(items, heading="Questions"):
    rows = "".join(f'<details class="faq"{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(items))
    return f'''<section class="g g-day section" id="faq"><div class="wrap faq-grid"><h2>{E(heading)}</h2>
<div class="faq-list reveal">{rows}</div></div></section>'''


def contact_field(ctx):
    user, dom = B["email"].split("@")
    return f'''<section class="g g-sun section contact" id="contact"><div class="wrap contact-grid">
<div class="contact-copy"><h2>Get a price by morning</h2><p class="lead">Email or text your square footage and how many nights a week. We reply with a price by the next morning.</p></div>
<div class="contact-ways"><a class="mail-line" href="mailto:{B["email"]}?subject=Cleaning%20quote">{E(user)}@<wbr>{E(dom)}</a>
<a class="phone num" href="tel:{B["phone_e164"]}">{E(B["phone_display"])}</a>
{ctas(ctx, ("Capability statement", ctx.href("one-pager")), on_light=True)}</div>
</div></section>'''


def link_band(ctx, heading, groups):
    cols = "".join(f'<div><h3>{E(t)}</h3><ul class="link-list">{"".join(f"<li><a href={chr(34)}{h}{chr(34)}>{E(n)}</a></li>" for n, h in links)}</ul></div>' for t, links in groups)
    return f'<section class="g g-day section tight"><div class="wrap"><h2 class="visually-hidden">{E(heading)}</h2><div class="link-cols">{cols}</div></div></section>'


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
NAV = [("services", "Services"), ("areas", "Areas"), ("pricing", "Pricing"), ("faq", "FAQ")]


def nav_href(ctx, k):
    if k == "services":
        return ctx.href("index", "#services")
    if k == "areas":
        return ctx.href("index", "#areas")
    return ctx.href(k)


def wordmark(ctx):
    return f'<a class="wordmark" href="{ctx.href("index")}">{MARK}<span>Clean by Morning</span></a>'


def header(ctx, active):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{nav_href(ctx, k)}"{cur if k == active else ""}>{n}</a>' for k, n in NAV)
    menu = "".join(f'<a href="{ctx.href("svc:" + s["key"])}">{E(s["name"])}</a>' for s in SERVICES)
    menu += "".join(f'<a href="{ctx.href("area:" + a["slug"])}">{E(a["name"])}</a>' for a in AREAS)
    menu += (f'<a href="{ctx.href("pricing")}">Pricing</a><a href="{ctx.href("faq")}">FAQ</a><a href="{ctx.href("guides")}">Guides</a>'
             f'<a href="{ctx.href("about")}">About</a><a href="tel:{B["phone_e164"]}">Call {E(B["phone_display"])}</a>')
    bar = ""
    if ctx.preview:
        bar = ('<div class="g g-sun preview-bar"><div class="wrap"><strong>Preview</strong><span>The walkthrough form opens an email until a form service is connected.</span>'
               '<a href="one-pager.html">Capability statement</a></div></div>')
    return f'''{bar}<header class="g g-dusk site-header"><div class="wrap bar">
{wordmark(ctx)}
<nav class="nav" aria-label="Main">{links}<a class="num" href="tel:{B["phone_e164"]}">{E(B["phone_display"])}</a></nav>
<a class="btn btn-sun header-cta" href="{ctx.href("walkthrough")}">Book a walkthrough</a>
<details class="menu"><summary>Menu</summary><nav class="menu-panel g g-night" aria-label="Menu">{menu}</nav></details>
</div></header>'''


def footer(ctx):
    def col(title, links):
        return f'<nav class="foot-col" aria-label="{E(title)}"><h2>{E(title)}</h2>{"".join(f"<a href={chr(34)}{h}{chr(34)}>{E(n)}</a>" for n, h in links)}</nav>'
    svc = [(s["name"], ctx.href("svc:" + s["key"])) for s in SERVICES]
    areas = [(a["name"], ctx.href("area:" + a["slug"])) for a in AREAS] + [(u.split("//")[-1].split("/")[0], u) for u in B["same_as"]]
    company = [("Pricing", ctx.href("pricing")), ("FAQ", ctx.href("faq")), ("Guides", ctx.href("guides")), ("About", ctx.href("about")),
               ("Book a walkthrough", ctx.href("walkthrough")), ("Capability statement", ctx.href("one-pager"))]
    return f'''<footer class="g g-night site-footer"><div class="wrap">
<div class="foot-grid"><div class="foot-brand">{wordmark(ctx)}<p>Evening cleaning for medical, dental and office spaces in Brooklyn, Manhattan and Nassau County.</p>
<p>{E(B["cleaning_hours"])}.<br>{E(B["office_hours"])}.</p></div>
{col("Services", svc)}{col("Areas", areas)}{col("Company", company)}</div>
<a class="phone-line num" href="tel:{B["phone_e164"]}">{E(B["phone_display"])}</a>
<div class="foot-meta"><a href="mailto:{B["email"]}">{E(B["email"])}</a><span>{E(B["city_line"])} · © {B["year"]} {E(B["legal_name"])}</span><span>{CREDITS}</span><a href="#main">Back to top</a></div>
</div></footer>'''


def action_bar(ctx):
    return (f'<div class="action-bar g g-night"><a class="btn btn-ghost" href="tel:{B["phone_e164"]}">Call</a>'
            f'<a class="btn btn-sun" href="{ctx.href("walkthrough")}">Book a walkthrough</a></div>')


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
<meta property="og:image" content="{B["domain"]}/img/og-cover.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Clean by Morning: you lock up, we clean"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0034eb">
<link rel="icon" href="{ctx.asset("favicon.svg")}" type="image/svg+xml"><link rel="apple-touch-icon" href="{ctx.asset("apple-touch-icon.png")}">
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
# Pages
# ---------------------------------------------------------------------------
def home(ctx, wrapper=True):
    proof = proof_lines()
    clients = f'<p class="small">Clients include {E(", ".join(PROOF["clients"]))}.</p>' if PROOF["clients"] else ""
    proof_html = f'<ul class="checks proof">{"".join(f"<li>{E(x)}</li>" for x in proof)}</ul>' if proof else ""
    body = f'''<section class="g g-dusk hero"><div class="wrap hero-grid">
<div class="hero-copy"><h1>Medical offices, clean by morning</h1><span class="horizon" aria-hidden="true"></span>
<p class="lead">Evening cleaning for medical, dental and office spaces in Brooklyn, Manhattan and Nassau County. You lock up at 6. We're done before you open.</p>
{ctas(ctx, ("See prices", "#pricing"))}{proof_html}{clients}</div>
<figure class="ph tint hero-photo shutter">{ctx.img("windows", lazy=False)}<figcaption class="clock" data-clock>We clean between 6 PM and 2 AM, after you close.</figcaption></figure>
</div></section>
{night_sheet(ctx)}
{services_list(ctx)}
{price_band(ctx, f'From <span class="price-block num">${PRICING["min_visit"]}</span> a night', f"About ${PRICING['hourly']} per cleaning hour, with supplies included. Monthly autopay, month to month, 30 days' notice to cancel.")}
{areas_band(ctx)}
{faq_table(FAQ[:6])}
{contact_field(ctx)}'''
    return page(ctx, "index", "Medical & Office Cleaning NYC and Long Island | Clean by Morning",
                f"Evening cleaning for medical, dental and office spaces in Brooklyn, Manhattan and Nassau County. From ${PRICING['min_visit']} a visit, month to month. Book a walkthrough.",
                body, schema=[business_schema(), faq_schema(FAQ[:6])], wrapper=wrapper)


def service_page(ctx, s):
    trail = [("index", "Home"), ("svc:" + s["key"], s["name"])]
    nightly = "".join(f"<li>{E(x)}</li>" for x in s["nightly"])
    clinical = "".join(f"<li>{E(x)}</li>" for x in s["clinical"])
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
    second = "Every visit" if s["kind"] != "postcon" else "What we clean"
    body = f'''{page_head(ctx, s["name"], s["h1"], s["lead"], photo, ("Estimate the price", "#estimate"))}
<section class="g g-day section"><div class="wrap split reveal"><div>{sec_head(second, "The checklist we start from. We adjust it to your space at the walkthrough.")}</div><ul class="checks big">{nightly}</ul></div></section>
<section class="g g-night section"><div class="wrap">{sec_head("How we work")}<ul class="tiles reveal">{clinical}</ul></div></section>
{price_band(ctx, price_line, price_note, s["kind"], "estimate")}
{faq_table(s["faq"], "Questions about " + s["name"].lower())}
{link_band(ctx, "Related", [("Where we do it", [(f'{s["name"]} in {a["name"]}', ctx.href("area:" + a["slug"])) for a in AREAS]),
                            ("Other services", [(o["name"], ctx.href("svc:" + o["key"])) for o in SERVICES if o is not s])])}
{contact_field(ctx)}'''
    return page(ctx, "svc:" + s["key"], s["title"], s["lead"][:155], body, active="services",
                schema=[schema, crumbs_schema(ctx, trail), faq_schema(s["faq"])])


def area_page(ctx, a):
    trail = [("index", "Home"), ("area:" + a["slug"], a["name"])]
    paras = "".join(f"<p>{E(p)}</p>" for p in a["body"])
    hoods = ", ".join(a["hoods"][:-1]) + " and " + a["hoods"][-1]
    schema = business_schema() | {"areaServed": {"@type": "Place", "name": a["name"] + ", NY"}}
    photo = "morning" if a["slug"] == "nassau-county" else ("bridge" if a["slug"] == "brooklyn" else "windows")
    trio = "".join(fig(ctx, k) for k in ("rain", "lamp", "bridge", "windows", "morning") if k != photo)
    body = f'''{page_head(ctx, a["name"], a["h1"], a["lead"], photo, ("See prices", ctx.href("pricing")))}
<section class="g g-day section"><div class="wrap split reveal"><div>{sec_head("Cleaning in " + a["name"])}</div><div class="prose">{paras}</div></div></section>
<section class="g g-night section"><div class="wrap"><p class="names reveal">In {E(a["name"])} we clean in {E(hoods)}.</p><div class="photo-strip">{trio}</div></div></section>
{services_list(ctx, "Services in " + a["name"], "The same checklist and the same monthly pricing in every neighborhood.")}
{link_band(ctx, "Other areas", [("We also serve", [(o["name"], ctx.href("area:" + o["slug"])) for o in AREAS if o is not a]), ("Prices", [("Price list", ctx.href("pricing")), ("Estimate yours", ctx.href("pricing", "#estimate"))])])}
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
    body = f'''{page_head(ctx, "Pricing", "Office cleaning prices", "Monthly prices for evening cleaning in Brooklyn, Manhattan and Nassau County, before tax. Billed once a month by autopay.", "rain", ("Estimate yours", "#estimate"))}
<section class="g g-day section"><div class="wrap">{sec_head("Prices by size", "Monthly, before tax, for a typical number of restrooms at each size.")}
<div class="table-scroll reveal"><table class="price-table"><thead><tr><th>Space and schedule</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="note">Monthly figures assume {PRICING["weeks_per_month"]} weeks a month and 1–4 restrooms by size. New York sales tax applies to commercial cleaning. Your exact price comes after a 15-minute walkthrough.</p>
</div></section>
{price_band(ctx, "Your price, in a minute", f"Pick your space, size and nights. The same model as the table: about ${PRICING['hourly']} per cleaning hour with a ${PRICING['min_visit']} minimum a visit.", "medical", "estimate")}
<section class="g g-night section"><div class="wrap">{sec_head("How billing works")}<ul class="tiles reveal">
<li>One monthly price, billed on the 1st by ACH autopay</li><li>First month paid before the first clean</li><li>Month to month, with 30 days' notice to cancel</li>
<li>One-time jobs: {int(PRICING["deposit"] * 100)}% deposit to book, the rest on completion</li></ul></div></section>
{contact_field(ctx)}'''
    return page(ctx, "pricing", "Office Cleaning Prices NYC & Long Island | Clean by Morning",
                f"Monthly prices for medical, dental, office and gym cleaning in Brooklyn, Manhattan and Nassau County. From ${PRICING['min_visit']} a visit.",
                body, active="pricing", schema=[crumbs_schema(ctx, trail)])


def walkthrough_page(ctx):
    trail = [("index", "Home"), ("walkthrough", "Book a walkthrough")]
    opts = "".join(f"<option>{E(s['name'])}</option>" for s in SERVICES)
    body = f'''<section class="g g-dusk head"><div class="wrap head-grid form-grid">
<div class="head-copy">{crumbs(ctx, "Book a walkthrough")}<h1>Book a 15-minute walkthrough</h1><span class="horizon" aria-hidden="true"></span>
<p class="lead">We look at the space, agree on the checklist and send a fixed monthly price by the next morning.</p>
<ul class="checks"><li>Free, with no obligation</li><li>Before or after your hours, whichever suits you</li><li>Price in writing within 24 hours</li><li>Most clients can start within a week</li></ul>
<p>Rather talk? Call or text <a href="tel:{B["phone_e164"]}" class="num">{E(B["phone_display"])}</a>.</p></div>
<form class="form" data-walkthrough novalidate aria-label="Walkthrough request">
<div class="field"><label for="w-name">Your name</label><input id="w-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="w-company">Practice or company</label><input id="w-company" name="company" type="text" autocomplete="organization"></div>
<div class="field"><label for="w-email">Email</label><input id="w-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="w-phone">Phone</label><input id="w-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field"><label for="w-type">Type of space</label><select id="w-type" name="type">{opts}</select></div>
<div class="field"><label for="w-address">Address or neighborhood</label><input id="w-address" name="address" type="text" autocomplete="street-address"></div>
<div class="field"><label for="w-sqft">Approximate square feet</label><input id="w-sqft" name="sqft" type="text" inputmode="numeric"></div>
<div class="field"><label for="w-notes">Nights a week, and anything else</label><textarea id="w-notes" name="notes"></textarea></div>
<button class="btn btn-cobalt" type="submit">Request a walkthrough</button><p class="form-msg" data-form-msg role="status"></p>
</form></div></section>'''
    return page(ctx, "walkthrough", "Book a Cleaning Walkthrough | Clean by Morning",
                "Book a free 15-minute walkthrough for medical, dental or office cleaning in Brooklyn, Manhattan or Nassau County. Price in writing within 24 hours.",
                body, schema=[crumbs_schema(ctx, trail)])


def faq_page(ctx):
    trail = [("index", "Home"), ("faq", "FAQ")]
    body = f'''{page_head(ctx, "FAQ", "Commercial cleaning questions", "Prices, schedules, keys and alarms, payment and contracts: the questions to ask before you sign with any cleaner.", "morning")}
{faq_table(FAQ, "Questions")}
{contact_field(ctx)}'''
    return page(ctx, "faq", "Commercial Cleaning FAQ | Clean by Morning",
                "Answers about Clean by Morning's evening office and medical cleaning: prices, schedules, keys and alarms, payment and contracts.",
                body, active="faq", schema=[faq_schema(FAQ), crumbs_schema(ctx, trail)])


def owner_section(ctx):
    if not B["owner_name"]:
        return ""
    photo = ""
    if B["owner_photo"]:
        photo = (f'<figure class="ph owner-photo"><img src="{ctx.asset("img/" + B["owner_photo"])}" alt="{E(B["owner_name"])}, owner of Clean by Morning" '
                 f'width="800" height="1000" loading="lazy" decoding="async"></figure>')
    bio = f'<p class="lead">{E(B["owner_bio"])}</p>' if B["owner_bio"] else ""
    return f'''<section class="g g-dawn section" id="owner"><div class="wrap split reveal"><div class="prose">
<h2>{E(B["owner_name"])}, owner</h2>{bio}
<p>Call or text me directly at <a class="num" href="tel:{B["phone_e164"]}">{E(B["phone_display"])}</a>.</p></div>{photo}</div></section>'''


def about_page(ctx):
    trail = [("index", "Home"), ("about", "About")]
    body = f'''{page_head(ctx, "About", "One crew, one checklist", "Clean by Morning is an owner-operated cleaning company for medical practices and small offices in New York City and Nassau County.", "windows")}
<section class="g g-day section"><div class="wrap split reveal"><div>{sec_head("Why we work this way")}</div><div class="prose">
<p>The usual complaints about commercial cleaners are a different person every month, a checklist nobody follows, and an invoice that keeps changing. Clean by Morning is set up to avoid all three.</p>
<p>The owner cleans or inspects every account. Every visit follows the same written checklist. Prices are fixed and billed once a month, and you can leave with 30 days' notice.</p>
<p>We clean in the evening, after you close, so your patients and staff never see us, only the result.</p></div></div></section>
{owner_section(ctx)}
<section class="g g-night section"><div class="wrap">{sec_head("What you can count on")}<ul class="tiles reveal">
<li>A written checklist for your space, agreed at the walkthrough</li><li>Photos of every room after each clean, if you want them</li>
<li>Keys and alarm codes stored securely; the alarm set when we leave</li><li>One fixed monthly price, month to month</li></ul>
<div class="photo-strip">{fig(ctx, "bridge")}{fig(ctx, "lamp")}{fig(ctx, "rain")}</div></div></section>
{contact_field(ctx)}'''
    return page(ctx, "about", "About Clean by Morning | NYC Office Cleaning",
                "Clean by Morning is an owner-operated evening cleaning company for medical practices and small offices in NYC and Nassau County.",
                body, schema=[crumbs_schema(ctx, trail)])


def one_pager(ctx):
    proof = proof_lines() or ["Certificate of insurance sent on request once coverage is in place"]
    body = f'''<section class="g g-day section one-pager"><div class="wrap">
<h1>Capability statement</h1><span class="horizon" aria-hidden="true"></span>
<p class="lead">{E(B["legal_name"])}: evening commercial cleaning for medical offices, dental practices, offices and gyms in Brooklyn, Manhattan and Nassau County.</p>
<div class="op-grid"><div><h2>Services</h2><ul class="checks">{"".join(f"<li>{E(s['name'])}</li>" for s in SERVICES)}</ul>
<h2>How we work</h2><ul class="checks"><li>Owner-operated; the owner cleans or inspects every account</li><li>Written checklist per site; photos after each visit on request</li>
<li>Color-coded microfiber and EPA-registered disinfectants</li><li>No handling of sharps or regulated medical waste</li><li>Keys and alarm codes stored securely</li></ul></div>
<div><h2>Commercial terms</h2><ul class="checks"><li>Fixed monthly price, ACH autopay on the 1st</li><li>Month to month, 30 days' notice</li>
<li>From ${PRICING["min_visit"]} per visit; about ${PRICING["hourly"]} per cleaning hour</li><li>NAICS 561720, Janitorial Services</li>{"".join(f"<li>{E(x)}</li>" for x in proof)}</ul>
<h2>Contact</h2><p>{E(B["email"])}<br><span class="num">{E(B["phone_display"])}</span><br>{E(B["domain"].replace("https://", ""))}</p></div></div>
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
    secs = "".join(f'<h2>{E(h)}</h2><ul class="checks">{"".join(f"<li>{E(x)}</li>" for x in items)}</ul>' for h, items in g["sections"])
    schema = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["meta"],
              "author": {"@type": "Organization", "name": B["name"]}, "publisher": {"@id": B["domain"] + "/#business"},
              "mainEntityOfPage": ctx.canonical(key), "image": B["domain"] + "/img/" + PHOTOS["windows"]["file"]}
    others = [(o["title"], ctx.href("guides/" + o["slug"])) for o in GUIDES if o is not g]
    body = f'''{page_head(ctx, "Guides", g["title"], g["lead"], "windows", ("See prices", ctx.href("pricing")))}
<section class="g g-day section"><div class="wrap"><article class="article reveal">{secs}
<p>Want this checklist for your own office, priced? <a href="{ctx.href("walkthrough")}">Book a 15-minute walkthrough</a>.</p></article></div></section>
{link_band(ctx, "More guides", [("More guides", others), ("Services", [(s["name"], ctx.href("svc:" + s["key"])) for s in SERVICES[:3]])])}
{contact_field(ctx)}'''
    return page(ctx, key, f'{g["title"]} | Clean by Morning', g["meta"], body, schema=[schema, crumbs_schema(ctx, trail)])


def guides_index(ctx):
    trail = [("index", "Home"), ("guides", "Guides")]
    items = "".join(f'<li><a href="{ctx.href("guides/" + g["slug"])}"><span class="svc-name">{E(g["title"])}</span><span class="svc-line">{E(g["meta"])}</span><span class="svc-price">Read</span></a></li>' for g in GUIDES)
    body = f'''{page_head(ctx, "Guides", "Guides for office managers", "Plain answers about commercial cleaning in New York: what it costs, what it should include, and how often you need it.", "morning")}
<section class="g g-day section"><div class="wrap"><ul class="svc-list reveal">{items}</ul></div></section>
{contact_field(ctx)}'''
    return page(ctx, "guides", "Commercial Cleaning Guides | Clean by Morning",
                "Guides for NYC and Long Island office managers: cleaning costs, medical office checklists and how often to clean a dental office.",
                body, schema=[crumbs_schema(ctx, trail)])


def not_found(ctx):
    body = f'''<section class="g g-dusk head"><div class="wrap"><h1>Page not found</h1><span class="horizon" aria-hidden="true"></span>
<p class="lead">That page doesn't exist. Try the home page or book a walkthrough.</p>{ctas(ctx, ("Home", ctx.href("index")))}</div></section>'''
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
    for f in ("apple-touch-icon.png", "icon-512.png"):
        shutil.copy(ROOT / "static" / f, dest / f)
    write(dest / "favicon.svg", FAVICON)
    # Cloudflare Pages: long caching for fonts and images, basic security headers everywhere
    write(dest / ".htaccess", HTACCESS)
    write(dest / "_headers", "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
          "/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/img/*\n  Cache-Control: public, max-age=2592000\n")


# DreamHost (Apache): force https and www, the 404 page, no folder listings, caching
HTACCESS = """Options -Indexes
ErrorDocument 404 /404.html
DirectoryIndex index.html

RewriteEngine On
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^www\\. [NC]
RewriteCond %{HTTP_HOST} ^(?:www\\.)?(.+)$ [NC]
RewriteRule ^ https://www.%1%{REQUEST_URI} [L,R=301]

<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  <FilesMatch "\\.(woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.(webp|jpg|png|svg)$">
    Header set Cache-Control "public, max-age=2592000"
  </FilesMatch>
  <FilesMatch "\\.(css|js)$">
    Header set Cache-Control "public, max-age=86400"
  </FilesMatch>
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/plain
</IfModule>
"""


def launch_warnings():
    out = []
    if "555-01" in B["phone_display"]:
        out.append("phone is still the 555 placeholder: prospects who look you up will call it")
    if not B["form_endpoint"]:
        out.append("form_endpoint is empty: the walkthrough form opens an email app instead of sending")
    if not B["same_as"]:
        out.append("same_as is empty: add your Google Business Profile and LinkedIn URLs")
    if not B["owner_name"]:
        out.append("owner_name is empty: the About page shows no person")
    return out


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
    for w in launch_warnings():
        print("BEFORE LAUNCH:", w)


if __name__ == "__main__":
    build()
