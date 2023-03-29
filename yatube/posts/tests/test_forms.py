import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Comment
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_COUNT_TWO = 2
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post и перенаправляет на страницу
        автора поста."""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': 'Тут написан текст поста',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), POST_COUNT_TWO)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тут написан текст поста',
                image='posts/small.gif').exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': 'Тут написан текст поста',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                author=self.user,
                text='Тут написан текст поста',
                image='posts/small_2.gif').exists()
        )

    def test_auth_comment_create(self):
        """Авторизованный пользователь может оставить комментарии."""
        form_data = {
            'text': 'Комментарий к посту',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertContains(response, form_data['text'])
        self.assertEqual(len(Comment.objects.all()), 1)

    def test_guest_cannot_create_comment(self):
        """Неавторизованный пользователь не может оставить комментарии"""
        comments = set(Comment.objects.all())
        form_data = {
            'text': 'Комментарий к посту',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(set(Comment.objects.all()), comments)
