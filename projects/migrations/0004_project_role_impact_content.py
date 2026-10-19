"""
Content migration: "My role / Impact / Stack" for the four portfolio projects.

Facts come only from the resume experience entries and the existing project
pages. Fields are filled only when empty, so edits made in admin win; stack
tags are only added, never removed. Missing projects are skipped.

Project ↔ employer mapping confirmed by the owner (2026-10-19): Princess
Cruises = Mercury Development, Scorpion CRM = Distillery's "B2B CRM
California" client.
"""

from django.db import migrations
from django.utils.text import slugify

CONTENT = {
    "nyle": {
        "role": "AI-Native Frontend Architect at Nyle (Nov 2025 – present)",
        "impact": [
            "Designed the layered architecture (Components → Hooks → RTK Query → Effect services → ReScript core) and moved the product onto it while feature work continued.",
            "Restructured a 5-year-old SPA into a pnpm + Turborepo monorepo: product app, GraphQL BFF, landing, product demo, Storybook and shared packages.",
            "Moved business logic into a pure ReScript domain core: 130+ modules, 10 finite state machines.",
            "Made every backend type generated from the OpenAPI spec (osury + Sury decoders), so API changes surface as compile errors.",
            "Built @nyle/ui on Radix + Tailwind: about 70 components and 340+ Storybook stories, replacing antd page by page.",
            "Shipped the analytics canvas, P&L and Market Intelligence tables, supply-chain scheduler, RBAC, OAuth integrations (Amazon, Google Ads, Meta, Shopify) and an AI chat assistant over WebSocket.",
            "Added OpenTelemetry tracing (Collector, Tempo, Grafana) and used production traces to find the root causes of slow pages.",
            "Wrote 49 ADRs and turned code-review findings into 20 machine-readable rules for AI coding agents.",
        ],
        "tags": ["React", "TypeScript", "RTK Query", "GraphQL", "Storybook", "Tailwind CSS", "Radix UI", "OpenTelemetry"],
    },
    "princess-cruises-mobile": {
        "role": "Senior React Native Developer at Mercury Development (Oct 2024 – Oct 2025)",
        "impact": [
            "Led development of the React Native app across pre-cruise planning, in-cruise services and excursion management, with full accessibility compliance.",
            "Moved a mature, large-scale app from legacy data fetching to GraphQL with Relay; integrated the Relay client into the core infrastructure.",
            "Negotiated API contracts and schema design between the mobile and backend teams.",
            "Migrated the app to the React Native New Architecture.",
            "Set up automated code generation and tuned the React Native CI/CD pipelines.",
            "Mentored the team on GraphQL and state-management practices.",
        ],
        "tags": ["React Native", "GraphQL", "Relay"],
    },
    "scorpion-crm-mobile": {
        "role": "Senior React Native Developer → Team Lead at Distillery (2019 – 2022)",
        "impact": [
            "Worked with the US client for 3 years; the team delivered and maintained 2 cross-platform React Native apps.",
            "Led the team: interviews, task distribution, technical specifications and day-to-day client communication.",
            "Stayed hands-on: performance optimization, reusable generic chart and data modules on FP-TS, releases and CI/CD.",
        ],
        "tags": ["React Native", "GraphQL", "FP-TS"],
    },
    "osury-openapi-codegen": {
        "role": "Author and maintainer (open source)",
        "impact": [
            "Designed one intermediate representation that drives four targets: ReScript with Sury schemas, Effect TS, OCaml and Rust.",
            "Runs in production at Nyle, where every backend type in the ReScript domain core is generated rather than hand-written.",
            "Every target emits its own runtime decoders; errors carry a JSON path, a typed kind and a fix hint.",
            "CI compiles every target with its own toolchain and decodes sample data generated from the same spec.",
        ],
        "tags": [],
    },
}


def forwards(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Tag = apps.get_model("projects", "Tag")

    for slug, content in CONTENT.items():
        project = Project.objects.filter(slug=slug).first()
        if project is None:
            continue

        changed = []
        if not project.role:
            project.role = content["role"]
            changed.append("role")
        if not project.impact:
            project.impact = "\n".join(content["impact"])
            changed.append("impact")
        if changed:
            project.save(update_fields=changed)

        for name in content["tags"]:
            tag = Tag.objects.filter(name=name).first() or Tag.objects.filter(slug=slugify(name)).first()
            if tag is None:
                tag = Tag.objects.create(name=name, slug=slugify(name))
            project.tags.add(tag)


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_project_role_impact"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
