from django import forms
from django.test import Client, TestCase
from django.urls import reverse


class UserURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup_urls_uses_matching_template(self):
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_page_contains_transmitted_field(self):
        """Типы полей формы регистрации в словаре context соответствуют
        ожиданию"""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
