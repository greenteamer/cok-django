"""
Site identity: the one place for name, positioning, contacts and availability.

Every template gets these values as `identity` (see
`config.context_processors.identity`), and the PDF resume
(`resume/pdf_generator.py`) reads them too, so the name, headline and contact
links never drift between the home page, /resume/ and /resume.pdf.

Contacts that are `None` or empty are not rendered anywhere. See
`docs/modules/site-identity.md`.
"""

NAME = "Aleksander Korovkin"

# Positioning. HEADLINE is the <title>/og:title suffix and the PDF subtitle;
# VALUE_PROP is the first line under the name on the home page and /resume/.
HEADLINE = "Senior React Native & React Engineer"
VALUE_PROP = (
    "Senior React Native & React engineer, building mobile apps since 2016. "
    "I ship the web and backend side when the product needs it."
)
ENGAGEMENT = "Full- or part-time contract, US–EU time zones"
TOOLING_LINE = (
    "I also build type-safe developer tooling — osury, the OpenAPI codegen "
    "that generates every API type at Nyle."
)
META_DESCRIPTION = (
    "Aleksander Korovkin — remote React Native contractor and senior React "
    "engineer. React Native, Expo, TypeScript, GraphQL, Node.js. Contract or "
    "fractional mobile lead for US and EU teams."
)

LOCATION = "Batumi, Georgia · remote"
EMAIL = "hello@coreofkeen.com"
LINKEDIN_URL = "https://www.linkedin.com/in/aleksandr-korovkin/"
GITHUB_URL = "https://github.com/greenteamer"
SITE_URL = "https://coreofkeen.com"

# Optional booking link (cal.com / Calendly). None hides every "Book a call"
# button; email is the primary CTA either way.
CALENDAR_URL = None
# TODO(owner): Telegram handle without "@". None hides the link.
TELEGRAM_HANDLE = None

# Shown in the Contact block, the resume header and the PDF.
# Invoicing is B2B through a Georgian individual entrepreneur (IE) registration.
AVAILABILITY = "Open to full-time or part-time contracts · B2B invoice (Georgian IE) · US–EU time zones"

# Testimonials render on the home page only when this list is non-empty.
# Each item: {"quote": "...", "name": "...", "role": "Title, Company", "url": optional}
# TODO(owner): 2–3 quotes from former leads (Mercury Development, TSS Paratransit, Distillery).
TESTIMONIALS = []


def as_dict():
    telegram_url = f"https://t.me/{TELEGRAM_HANDLE}" if TELEGRAM_HANDLE else None
    return {
        "name": NAME,
        "headline": HEADLINE,
        "value_prop": VALUE_PROP,
        "engagement": ENGAGEMENT,
        "tooling_line": TOOLING_LINE,
        "meta_description": META_DESCRIPTION,
        "location": LOCATION,
        "email": EMAIL,
        "linkedin_url": LINKEDIN_URL,
        "github_url": GITHUB_URL,
        "site_url": SITE_URL,
        "calendar_url": CALENDAR_URL,
        "telegram_handle": TELEGRAM_HANDLE,
        "telegram_url": telegram_url,
        "availability": AVAILABILITY,
        "testimonials": TESTIMONIALS,
    }
