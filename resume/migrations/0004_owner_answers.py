"""
Content migration: facts confirmed by the owner on 2026-10-19.

- Distillery "Senior React Native Developer": real description (was just the
  title) and end date Sep 2020, so it no longer overlaps "Company Team Lead"
  (Oct 2020 – Dec 2022)
- Storiqa ends Dec 2018, so 2019 reads GMCS (Jan–Jun) -> Distillery (Jul)
- Mercury Development: New Architecture migration bullet
- Summary: "7+ years of React Native" -> "8+ years" (RN since Aug 2016)
- Languages: Russian (native), English (C1)

Runs on the active profile only, matches rows by company/position, skips
what is missing, idempotent. See docs/modules/resume.md.
"""

import datetime

from django.db import migrations

DISTILLERY_SENIOR_DESCRIPTION = (
    "<ul>"
    "<li>Optimized the performance of the client&#39;s React Native apps.</li>"
    "<li>Designed reusable, generic chart and data modules built on FP-TS.</li>"
    "<li>Owned releases and the CI/CD pipeline.</li>"
    "</ul>"
)

MERCURY_NEW_ARCH = (
    "<p><strong>New Architecture.</strong> Migrated the app to the React Native New Architecture.</p>"
)

LANGUAGES = [
    ("English", "C1, professional working"),
    ("Russian", "Native"),
]


def forwards(apps, schema_editor):
    Profile = apps.get_model("resume", "Profile")
    Language = apps.get_model("resume", "Language")

    profile = Profile.objects.filter(is_active=True).first()
    if profile is None:
        return
    experiences = profile.experiences.all()

    senior = experiences.filter(company__startswith="Distillery", position="Senior React Native Developer").first()
    if senior is not None:
        senior.end_date = datetime.date(2020, 9, 1)
        if "FP-TS" not in senior.description:
            senior.description = DISTILLERY_SENIOR_DESCRIPTION
        senior.save(update_fields=["end_date", "description"])

    storiqa = experiences.filter(company__startswith="Storiqa").first()
    if storiqa is not None:
        storiqa.end_date = datetime.date(2018, 12, 1)
        storiqa.save(update_fields=["end_date"])

    mercury = experiences.filter(company__startswith="Mercury Development").first()
    if mercury is not None and "New Architecture" not in mercury.description:
        mercury.description = mercury.description.rstrip() + "\n" + MERCURY_NEW_ARCH
        mercury.save(update_fields=["description"])

    if "7+ years of React Native" in profile.summary:
        profile.summary = profile.summary.replace("7+ years of React Native", "8+ years of React Native")
        profile.save(update_fields=["summary"])

    for order, (name, proficiency) in enumerate(LANGUAGES, start=1):
        Language.objects.update_or_create(
            profile=profile, name=name, defaults={"proficiency": proficiency, "order": order}
        )


class Migration(migrations.Migration):

    dependencies = [
        ("resume", "0003_recruiter_positioning"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
