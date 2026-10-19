"""
Content migration: recruiter-facing positioning for the active resume profile.

- Profile title: one headline matching config/identity.py
- Typos in summary/experience text ("peges", "standartisation")
- Skills: canonical names, mainstream-first order, and categories with
  niche depth moved to "Advanced / type-level"

Idempotent and safe on an empty database (no active profile -> no-op).
Only adds skills the resume text or the owner confirms: Expo (home hero),
Tailwind CSS (Nyle design system), Finite State Machines and OpenAPI
codegen (Nyle / TSS experience), New Architecture migration and EAS (owner).
See docs/modules/resume.md.
"""

from django.db import migrations

TITLE = "Senior React Native & React Engineer | Full- or part-time contract | US–EU time zones"

TYPOS = {
    "peges": "pages",
    "standartisation": "standardisation",
}

RENAMES = {
    "NextJS": "Next.js",
    "Node.Js": "Node.js",
    "Open Telemetry": "OpenTelemetry",
}

MOBILE = "Mobile"
FRONTEND = "Frontend"
BACKEND = "Backend & APIs"
DEVOPS = "DevOps & Observability"
ADVANCED = "Advanced / type-level"  # == resume.models.ADVANCED_SKILL_CATEGORY

# (name, category) in display order: the mainstream stack recruiters search for first.
SKILLS = [
    ("React Native", MOBILE),
    ("Expo", MOBILE),
    ("Reanimated", MOBILE),
    ("New Architecture migration", MOBILE),
    ("TypeScript", FRONTEND),
    ("React", FRONTEND),
    ("Next.js", FRONTEND),
    ("Node.js", BACKEND),
    ("GraphQL", BACKEND),
    ("Apollo", BACKEND),
    ("Relay", BACKEND),
    ("PostgreSQL", BACKEND),
    ("Redux", FRONTEND),
    ("RTK Query", FRONTEND),
    ("Storybook", FRONTEND),
    ("Tailwind CSS", FRONTEND),
    ("Docker", DEVOPS),
    ("GitHub Actions", DEVOPS),
    ("Fastlane", MOBILE),
    ("CodePush", MOBILE),
    ("TestFlight", MOBILE),
    ("EAS", MOBILE),
    ("OpenTelemetry", DEVOPS),
    ("Google Play", MOBILE),
    ("Mobile CI/CD & Delivery", MOBILE),
    ("JavaScript", FRONTEND),
    ("Radix UI", FRONTEND),
    ("Recharts", FRONTEND),
    ("PixiJS", FRONTEND),
    ("Vite", FRONTEND),
    ("Mobx", FRONTEND),
    ("Electron", FRONTEND),
    ("Django", BACKEND),
    ("Python", BACKEND),
    ("MySQL", BACKEND),
    ("MongoDB", BACKEND),
    ("SQL", BACKEND),
    ("Turborepo", DEVOPS),
    ("GitLab CI", DEVOPS),
    ("Grafana", DEVOPS),
    ("Nginx", DEVOPS),
    ("Linux", DEVOPS),
    ("ReScript", ADVANCED),
    ("Effect TS", ADVANCED),
    ("FP-TS", ADVANCED),
    ("OCaml", ADVANCED),
    ("Clojure", ADVANCED),
    ("Finite State Machines", ADVANCED),
    ("OpenAPI codegen", ADVANCED),
]

# Skills created when missing (all others are only re-ordered / re-categorized).
ADD_IF_MISSING = {
    "Expo",
    "Tailwind CSS",
    "Finite State Machines",
    "OpenAPI codegen",
    # Owner-confirmed 2026-10-19: migrated the last RN app (Mercury) to the New
    # Architecture (no deep JSI / Turbo Module work); some EAS, mostly bare RN.
    "New Architecture migration",
    "EAS",
}


def forwards(apps, schema_editor):
    Profile = apps.get_model("resume", "Profile")
    Skill = apps.get_model("resume", "Skill")

    profile = Profile.objects.filter(is_active=True).first()
    if profile is None:
        return

    profile.title = TITLE
    for wrong, right in TYPOS.items():
        profile.summary = profile.summary.replace(wrong, right)
    profile.save(update_fields=["title", "summary"])

    for exp in profile.experiences.all():
        description = exp.description
        for wrong, right in TYPOS.items():
            description = description.replace(wrong, right)
        if description != exp.description:
            exp.description = description
            exp.save(update_fields=["description"])

    skills = Skill.objects.filter(profile=profile)
    for old, new in RENAMES.items():
        if not skills.filter(name=new).exists():
            skills.filter(name=old).update(name=new)

    for order, (name, category) in enumerate(SKILLS, start=1):
        updated = skills.filter(name=name).update(category=category, order=order)
        if not updated and name in ADD_IF_MISSING:
            Skill.objects.create(profile=profile, name=name, category=category, order=order)

    # Anything not in the list (added in admin later) goes after the mainstream block.
    known = {name for name, _ in SKILLS}
    for offset, skill in enumerate(skills.exclude(name__in=known).order_by("order", "name")):
        skill.order = len(SKILLS) + 1 + offset
        skill.save(update_fields=["order"])


class Migration(migrations.Migration):

    dependencies = [
        ("resume", "0002_education_language"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
