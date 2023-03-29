from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('auth')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_are_available_to_any_user(self):
        desired_urls = [
            '/auth/signup/', '/auth/logout/', '/auth/login/',
            '/auth/password_reset/', '/auth/password_reset/done/',
            '/auth/reset/uidb64/token/', '/auth/reset/done/',
        ]
        for url in desired_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_is_available_to_an_authorized_user(self):
        desired_urls = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for url in desired_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_anonymous_on_auth_login(self):
        """Страница /password_change/ и /password_change/done/
        перенаправит анонимного пользователя на страницу логина."""
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/')
        response = self.guest_client.get('/auth/password_change/done/',
                                         follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/done/')

    def test_unexisting_page_url_does_not_exist(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/uidb64/token/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
