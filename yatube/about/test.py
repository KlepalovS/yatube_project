from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutUrlTests(TestCase):
    """Тесты Urls в About."""

    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_url_exists_at_desired_location(self):
        """Проверка доступности адресов статических страниц."""
        url_names = (
            '/about/author/',
            '/about/tech/',
        )
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress).status_code
                self.assertEqual(
                    response, HTTPStatus.OK.value
                )

    def test_static_pages_url_uses_correct_templates(self):
        """Проверка соответствия шаблона адресу статической страницы."""
        templates_url_names = {
            'about/about.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)


class AboutViewsTest(TestCase):
    """Тесты View в About."""

    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_names(self):
        """URLs, генерируемые при помощи имен namespace:name, доступны."""
        page_names = (
            'about:author',
            'about:tech',
        )
        for name in page_names:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_page_uses_correct_template(self):
        """При запросе к namespace:name применяются правильные шаблоны."""
        names_templates = {
            'about:author': 'about/about.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in names_templates.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
