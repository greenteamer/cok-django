# Site Identity, Contact Block and Testimonials

## Overview

**Purpose:** One place for the owner's name, positioning, contacts and availability, so the
home page, `/resume/`, project pages, `<title>`/OG tags and `/resume.pdf` always say the same thing.

**Files:**
- `config/identity.py` — the values (plain Python constants) and `as_dict()`
- `config/context_processors.py` — `identity()` exposes `as_dict()` to every template as `identity`
  (registered in `config/settings.py` → `TEMPLATES[0]["OPTIONS"]["context_processors"]`)
- `templates/_contact.html` — site-wide Contact block (`#contact`), included by `templates/base.html`
- `templates/_testimonials.html` — testimonials section, included by `templates/home.html`
- `static/css/sections/Contact.css`, `static/css/sections/Testimonials.css`

`resume/pdf_generator.py` imports `config.identity` directly.

---

## Values (`config/identity.py`)

| Constant | Used for |
|----------|----------|
| `NAME` | Navbar brand, home hero, `/resume/` H1, every `<title>` / `og:title` suffix, `og:site_name`, footer ©, PDF |
| `HEADLINE` | Default `<title>` = `NAME | HEADLINE`, home H1, PDF subtitle |
| `VALUE_PROP` | `/resume/` first line, PDF summary |
| `ENGAGEMENT` | Pill under the headline (home, `/resume/`), PDF subtitle |
| `TOOLING_LINE` | Second line about osury (home, `/resume/`, PDF summary) |
| `META_DESCRIPTION` | Default `meta description` / `og:description` / `twitter:description` (home, `/resume/`) |
| `LOCATION`, `EMAIL`, `LINKEDIN_URL`, `GITHUB_URL`, `SITE_URL` | Contact block, resume header, PDF |
| `CALENDAR_URL` | "Book a call" buttons/links — **optional, hidden while `None`** (email is the primary CTA) |
| `TELEGRAM_HANDLE` | Telegram link (without `@`) — **hidden while `None`** |
| `AVAILABILITY` | Availability pill (Contact block, `/resume/`) and PDF line |
| `TESTIMONIALS` | Testimonials section — **hidden while empty** |

Open `TODO(owner)` items in the file: Telegram handle, testimonial quotes. A calendar link is
optional and intentionally unset.

Engagement (owner, 2026-10-19): full- or part-time contracts, B2B invoice through a Georgian
individual entrepreneur (IE), US–EU time zones. No start date or weekly hours are shown.

### Positioning rules

- One value proposition everywhere: *Senior React Native & React engineer, mobile since 2016,
  web and backend when needed; full- or part-time contract, US–EU time zones.* Mobile work is
  described as mostly bare React Native, Expo when it fits. osury/tooling is the
  second line, never the headline.
- One name everywhere: **Aleksander Korovkin** (the LinkedIn URL slug `aleksandr-korovkin` is
  LinkedIn's, not displayed).
- Long-tail search phrases ("React Native contractor", "remote React Native engineer",
  "fractional mobile lead", "Expo") appear naturally in the hero, Contact block and meta — no
  keyword stuffing.
- No claims the resume does not back up.

---

## Contact Block (`templates/_contact.html`)

Rendered on **every page** above the footer, anchor `#contact`. Navbar "Contact", "Let's Talk →"
and page CTAs link to `#contact` (same page, no jump to the home page).

Contents: heading "Hiring a React Native contractor?", short pitch, availability pill,
buttons (Email with the address as text, "Book a 30-min call" when `CALENDAR_URL`,
"Resume (PDF)"), and a list: Email, Telegram (optional), Call (optional), LinkedIn, GitHub,
Location.

### Cloudflare Email Obfuscation

The site is behind Cloudflare with Email Address Obfuscation on, which rewrites addresses into
`[email protected]` + JS. Every visible address is wrapped in `<!--email_off-->…<!--/email_off-->`
so Cloudflare leaves it as plain text (recruiters copy it; no-JS clients and the HTML source
see it). Keep these comments when editing email markup.

---

## Testimonials (`templates/_testimonials.html`)

Shown on the home page after Featured Projects **only when** `TESTIMONIALS` is non-empty.
Item shape:

```python
{"quote": "…", "name": "Full Name", "role": "Title, Company", "url": "https://linkedin.com/in/…"}  # url optional
```

Plan: 2–3 quotes from former leads (Mercury Development, TSS Paratransit, Distillery).

---

## Footer

`templates/base.html` footer is now only the copyright bar: `© {% now "Y" %} NAME` (year is
dynamic) and links to the PDF, LinkedIn, GitHub. It shares the Contact gradient.

---

## Changing something

| Change | Where |
|--------|-------|
| Name, headline, pitch, contacts, availability | `config/identity.py` (redeploy) |
| Testimonials | `config/identity.py` `TESTIMONIALS` |
| Skills order / categories | Django admin (see [`resume.md`](./resume.md)) |
| Project role / impact | Django admin (see [`projects.md`](./projects.md)) |

---

**Last Updated:** 2026-10-19
