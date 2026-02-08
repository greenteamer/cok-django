from io import BytesIO
from pathlib import Path
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from PIL import Image

from .models import Post


class PostMarkdownTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="editor",
            password="test-password-123",
        )

    def test_markdown_is_rendered_to_html(self):
        post = Post.objects.create(
            title="Markdown title",
            author=self.user,
            content_markdown="# Heading\n\nSome **bold** text.",
        )

        self.assertIn("<h1>Heading</h1>", post.content)
        self.assertIn("<strong>bold</strong>", post.content)
        self.assertIn("Heading Some bold text.", post.excerpt)
        self.assertEqual(post.meta_title, "Markdown title")
        self.assertTrue(post.meta_description)

    def test_legacy_html_content_still_works(self):
        post = Post.objects.create(
            title="Legacy title",
            author=self.user,
            content="<p>Legacy content</p>",
        )

        self.assertEqual(post.content, "<p>Legacy content</p>")
        self.assertEqual(post.meta_title, "Legacy title")

    def test_unsafe_schemes_in_links_are_replaced(self):
        post = Post.objects.create(
            title="Unsafe links",
            author=self.user,
            content_markdown='[click](javascript:alert(1)) ![img](data:image/png;base64,abc)',
        )

        self.assertIn('href="#"', post.content)
        self.assertIn('src="#"', post.content)

    def test_code_quotes_are_not_double_escaped(self):
        post = Post.objects.create(
            title="Code quotes",
            author=self.user,
            content_markdown='and `@tag("_tag")`',
        )

        self.assertIn('<code>@tag("_tag")</code>', post.content)


class PostImageVariantTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="image-editor",
            password="test-password-123",
        )
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.override.enable()
        self.addCleanup(self.override.disable)

    def _make_upload(self, width=1200, height=800):
        buffer = BytesIO()
        Image.new("RGB", (width, height), color="#e2e8f0").save(buffer, format="JPEG")
        return SimpleUploadedFile(
            "featured.jpg",
            buffer.getvalue(),
            content_type="image/jpeg",
        )

    def test_featured_image_variants_are_cropped_to_expected_sizes(self):
        post = Post.objects.create(
            title="Post with featured image",
            author=self.user,
            content="<p>Image test</p>",
            featured_image=self._make_upload(),
        )

        card_url = post.featured_image_card_url
        hero_url = post.featured_image_hero_url

        self.assertTrue(card_url)
        self.assertTrue(hero_url)

        card_path = Path(settings.MEDIA_ROOT) / card_url.replace(settings.MEDIA_URL, "", 1)
        hero_path = Path(settings.MEDIA_ROOT) / hero_url.replace(settings.MEDIA_URL, "", 1)
        self.assertTrue(card_path.exists())
        self.assertTrue(hero_path.exists())

        with Image.open(card_path) as card_image:
            self.assertEqual(card_image.size, (800, 450))

        with Image.open(hero_path) as hero_image:
            self.assertEqual(hero_image.size, (1600, 900))
