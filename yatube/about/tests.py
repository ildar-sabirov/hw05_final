from django.test import Client, TestCase
from http import HTTPStatus

from django.urls import reverse


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        self.assertEqual(self.guest_client.get('/about/author/').status_code,
                         HTTPStatus.OK)
        self.assertEqual(self.guest_client.get('/about/tech/').status_code,
                         HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        self.assertTemplateUsed(self.guest_client.get('/about/author/'),
                                'about/author.html')
        self.assertTemplateUsed(self.guest_client.get('/about/tech/'),
                                'about/tech.html')

    def test_namespace_uses_correct_template(self):
        self.assertTemplateUsed(self.guest_client.get(reverse('about:author')),
                                'about/author.html')
        self.assertTemplateUsed(self.guest_client.get(reverse('about:tech')),
                                'about/tech.html')
