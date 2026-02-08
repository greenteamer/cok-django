from django.contrib.auth import get_user_model
from django.test import TestCase

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
