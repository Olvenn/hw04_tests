from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_static_pages_exists_at_desired_location(self):
        """Проверка доступности адресов статических страниц."""
        test_items = {
            'author': self.guest_client.get('/about/author/').status_code,
            'tech': self.guest_client.get('/about/tech/').status_code,
        }

        for field, expected_value in test_items.items():
            with self.subTest(field=field):
                self.assertEqual(
                    expected_value, 200)

    def test_static_pages_uses_correct_template(self):
        """Проверка шаблона для адресов статических страниц."""
        test_items = {
            'author': self.guest_client.get('/about/author/'),
            'tech': self.guest_client.get('/about/tech/'),
        }

        for field, expected_value in test_items.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    expected_value, f'about/{field}.html')
