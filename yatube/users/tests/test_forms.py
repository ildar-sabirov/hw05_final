import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import override_settings, TestCase, Client

from django.conf import settings
from django.urls import reverse

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пользователя."""
        form_data = {
            'username': 'AbraKatabra',
            'email': 'abra@katabra.com',
            'password1': 'passwordABRA',
            'password2': 'passwordABRA',
            'first_name': 'Abra',
            'last_name': 'Katabra'
        }
        self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            User.objects.filter(
                username='AbraKatabra',
                email='abra@katabra.com',
                first_name='Abra',
                last_name='Katabra').exists()
        )
