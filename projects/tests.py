from django.test import TestCase
from django.test.utils import override_settings

from .models import Project


@override_settings(CANONICAL_HOST="", SECURE_SSL_REDIRECT=False)
class HomeHeroTests(TestCase):
    def create_project(self, title, order, is_featured=True):
        return Project.objects.create(
            title=title,
            description="Demo",
            image=f"projects/{order}.webp",
            is_featured=is_featured,
            order=order,
        )

    def test_hero_fan_shows_first_three_featured_projects(self):
        for order, title in enumerate(["Alpha", "Bravo", "Charlie", "Delta"]):
            self.create_project(title, order)

        response = self.client.get("/")

        fan = response.content.decode().split('class="HeroWork"', 1)[1].split("</section>", 1)[0]
        self.assertEqual(fan.count('class="HeroWork__item"'), 3)
        self.assertIn('aria-label="Alpha"', fan)
        self.assertNotIn('aria-label="Delta"', fan)

    def test_proof_strip_lists_all_featured_projects_only(self):
        for order, title in enumerate(["Alpha", "Bravo", "Charlie", "Delta"]):
            self.create_project(title, order)
        self.create_project("Hidden", 10, is_featured=False)

        response = self.client.get("/")

        proof = response.content.decode().split('class="Hero__proof"', 1)[1].split("</p>", 1)[0]
        for title in ["Alpha", "Bravo", "Charlie", "Delta"]:
            self.assertIn(f">{title}</a>", proof)
        self.assertNotIn("Hidden", proof)

    def test_hero_has_no_fabricated_mockup_data(self):
        self.create_project("Alpha", 0)

        response = self.client.get("/")

        for fake in ["PhoneMockup", "Merged PR #42", "Launched New App", "50+"]:
            self.assertNotContains(response, fake)

    def test_hero_without_featured_projects_hides_fan_and_proof(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="HeroWork"')
        self.assertNotContains(response, 'class="Hero__proof"')
