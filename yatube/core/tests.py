from http import HTTPStatus

from django.test import Client, TestCase


class CorePagesTests(TestCase):
    def test_error_page(self):
        """URL-адрес использует соответствующий шаблон 404."""
        self.user_client = Client()
        response = self.user_client.get("/unknown_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
