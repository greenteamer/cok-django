from django.db import migrations, models


class Migration(migrations.Migration):
    """
    external_link mixed "live product" and "repository"; case_study_link ended
    up holding repositories. Rename keeps existing values in place.
    """

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(model_name="project", old_name="external_link", new_name="live_url"),
        migrations.RenameField(model_name="project", old_name="case_study_link", new_name="case_study_url"),
        migrations.AlterField(
            model_name="project",
            name="live_url",
            field=models.URLField(
                blank=True,
                help_text="The running product: App Store page, website or demo. Shown as “Live ↗”.",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="case_study_url",
            field=models.URLField(
                blank=True,
                help_text="A write-up about the project (article or blog post). Shown as “Case study ↗”.",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="source_url",
            field=models.URLField(blank=True, help_text="Source code repository. Shown as “Source ↗”."),
        ),
    ]
