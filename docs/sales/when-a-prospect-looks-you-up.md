# When a prospect looks you up

Most people who get a cold email check before they reply. They google the business name, open the website from the email signature, and look for a real person, a real phone number and some sign that other businesses use you. These are the things they check, in the order they check them.

## 1. Googling "Clean by Morning"

What should come up: your website first, your Google Business Profile panel on the right (on a phone, at the top), then your LinkedIn page.

- [ ] Website live at `cleanbymorning.com`, with the bare domain redirecting to `www` (Cloudflare → Rules → Redirect Rules)
- [ ] Google Search Console verified, `sitemap.xml` submitted, then use "Request indexing" on the home page. A new site usually shows up for its own name within a few days to two weeks
- [ ] Google Business Profile verified (service-area business, home address hidden). This is the panel with your phone, hours and reviews
- [ ] LinkedIn company page, plus your personal LinkedIn listing "Owner, Clean by Morning"
- [ ] Each profile URL added to `same_as` in `site/build.py`, then rebuild. This tells Google they all belong to the same business

## 2. Clicking the link in your email

- [ ] Every sending domain (`getcleanbymorning.com`, `cleanbymorningnyc.com`) redirects to `https://www.cleanbymorning.com`. If someone types the domain from your email address and gets an error, the email looks like spam
- [ ] The signature uses the main domain (`cleanbymorning.com`) for the website link, never a sending domain

## 3. On the website

The site already has a clear offer, prices, an estimator, an FAQ and a capability statement. It's missing the parts only you can add:

- [ ] **A real phone number** you or your voicemail answers (`phone_display` and `phone_e164`). The build prints a warning while it's still the 555 placeholder
- [ ] **Your name and photo** on the About page (`owner_name`, `owner_photo`, `owner_bio`). For an owner-operated business, a face is the strongest trust signal you have before you have reviews
- [ ] **A working form** (`form_endpoint`, e.g. Formspree). Without it the form opens the visitor's email app, which loses people on office computers
- [ ] **Insurance** turned on (`insured: True`) once the policy is bound. Medical offices and building managers will ask for a certificate

## 4. Proof, as you get it

You have none yet, and the site doesn't pretend otherwise. Add each item the week it becomes true:

- [ ] First Google review, after the first client's first month. Then `review_count` and `rating` in `PROOF`
- [ ] Client names, with written permission (`clients`)
- [ ] Your own photos of finished spaces (with permission, no patient areas showing screens or files)

## What ranks you for searches like "dental office cleaning Brooklyn"

The site is built correctly for this: one page per service and per area, unique titles and descriptions, structured data, a sitemap, fast pages. What decides ranking from here is mostly off the site:

1. **Google Business Profile.** For "near me" and "in Brooklyn" searches, the map results come almost entirely from the profile: category, reviews, photos, and how often you post.
2. **Reviews.** The number, how recent they are, and whether they mention the service and the neighborhood.
3. **Citations.** The same name, phone and website on Yelp, Bing Places, Apple Business Connect, BBB, Nextdoor and the Chamber of Commerce.
4. **Links.** A few local links matter more than many random ones: a Brooklyn or Nassau chamber listing, a BNI chapter, a building manager's vendor page, a client's "our partners" page.
5. **Time and content.** One new guide a month answering a question a prospect actually asked you.

Expect your name to rank within weeks. Competitive searches like "office cleaning Manhattan" take months, so cold email brings the first clients while this builds.
