# Clean by Morning: the next four weeks

Goal: by the end of week 4, the site is live and findable, outreach is running every weekday, and the first walkthroughs are booked.

## Week 1: foundations

- [ ] Buy `cleanbymorning.com`, plus 2 sending domains (`getcleanbymorning.com`, `cleanbymorningnyc.com`)
- [x] Business email `jamel@cleanbymorning.com` is set up (Cloudflare Email Routing: confirm you can send as it from Gmail, see README)
- [ ] On each sending domain, set up SPF, DKIM and DMARC, then start warming each inbox (10–20 emails a day, rising over 2–3 weeks)
- [ ] Search "Clean by Morning" in the NY Department of State entity database and the USPTO trademark search
- [ ] Decide the entity with an accountant: register your Florida LLC in New York, or form a New York LLC (both have a newspaper publication requirement), or start under an assumed name
- [ ] Get 3 general liability quotes ($1M/$2M); bind one before the first walkthrough
- [ ] Apply for a New York sales tax Certificate of Authority (at least 20 days before you invoice)
- [ ] Put your real phone number in `site/build.py`, connect a form service (Formspree or Basin) in `form_endpoint`, run `python3 site/build.py`
- [ ] Deploy `site/public` to Cloudflare Pages and connect the domain; redirect the bare domain and both sending domains to `https://www.cleanbymorning.com`
- [ ] Add your name, photo and short bio (`owner_name`, `owner_photo`, `owner_bio`) so prospects see a real person. See `docs/sales/when-a-prospect-looks-you-up.md`

## Week 2: get found

- [ ] Google Search Console: verify the domain, submit `sitemap.xml`
- [ ] Google Business Profile: service-area business (hide your home address), areas Brooklyn, Manhattan, Nassau County, primary category "Commercial cleaning service", description from `brand/BRAND.md`, profile and cover images from `brand/`
- [ ] Bing Places (import from Google) and Apple Business Connect
- [ ] Same name, phone and website on: Yelp, LinkedIn company page, Facebook page, Instagram, Nextdoor business page, BBB (optional), Thumbtack (optional)
- [ ] Add each profile URL to `same_as` in `site/build.py` and rebuild
- [ ] Add your Google Analytics id to `ga4_id` and rebuild

## Week 3: start outreach

- [ ] Build a list of 300–500 targets in one area first (medical and dental practices in one Brooklyn or Nassau neighborhood cluster)
- [ ] Load the sequences in `docs/sales/email-sequences.md`; start at 20–30 new contacts a day per inbox
- [ ] Drop in on 5–10 practices on your route each week with the printed capability statement (`/one-pager/`)
- [ ] Run every walkthrough with `docs/sales/walkthrough-and-closing.md`; send proposals within 24 hours

## Week 4: close and prove it

- [ ] Sign the first account: agreement, first month paid, autopay set
- [ ] First night: photos to the client; write the site checklist
- [ ] Track: emails sent, replies, walkthroughs, proposals, signed, monthly revenue. These numbers become your agency's case study.
- [ ] Once the policy is bound, set `insured: True` in `site/build.py` and rebuild
- [ ] Ask the first client for a Google review after their first month

## Every month after

- Add one guide page answering a question prospects asked you
- Add real before-and-after photos (with permission) and replace the stock city photos
- Ask every client for a review after their first month
- Add a neighborhood to an area page only when you actually clean there
