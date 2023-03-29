from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.core.cache import cache
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()
POST_AMOUNT_1 = 1
POST_AMOUNT_10 = 10
POST_AMOUNT_3 = 3
LAST_POST_COUNT_13 = 13
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('auth')
        cls.group = Group.objects.create(slug='first_slug')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тут находится текст поста',
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif', content=SMALL_GIF, content_type='image/gif')
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        def url(url, **kwargs):
            return reverse(url, kwargs=kwargs)

        urls = [
            url('posts:index'),
            url('posts:group_list', slug=self.group.slug),
            url('posts:profile', username=self.user.username),
            url('posts:post_detail', post_id=self.post.id),
            url('posts:post_edit', post_id=self.post.id),
            url('posts:post_create'),
        ]
        templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        ]
        for url, template in zip(urls, templates):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_page_contains_post(self):
        """На главной странице пользователь точно увидит единственный пост
        (создаём в `setUp`)"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.context['title'],
                         'Последние обновления на сайте')
        self.assertEqual(len(response.context['page_obj']), POST_AMOUNT_1)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_group_list_page_contains_group_post(self):
        """Создав пост (см `setUp`), увидим его на странице заданной группы"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), POST_AMOUNT_1)
        self.assertEqual(response.context['title'],
                         f'Записи сообщества {self.group}')
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_profile_page_contains_transmitted_context(self):
        """Создав пользователя (см `setUp`), увидим его на странице профиля"""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(response.context['username'], self.user.username)
        self.assertEqual(response.context['count'], self.user.posts.count())
        self.assertEqual(response.context['page_obj'][0].id, self.post.id)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_post_detail_contains_transmitted_context(self):
        """Создав пост (см `setUp`), увидим его подробную информацию
        на странице детального осмотра"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post_id'], self.post.id)
        self.assertEqual(response.context['post'].id, self.post.id)
        self.assertEqual(response.context['count'], self.user.posts.count())
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_create_post_page_contains_transmitted_field(self):
        """Типы полей формы создания поста в словаре context соответствуют
        ожиданию"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_contains_transmitted_field(self):
        """Типы полей формы редактирования поста в словаре context
        соответствуют ожиданию"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_visibility(self):
        """Создав пост (см `setUp`), увидим его на главной странице,
        странице выбранной группы и в профиле пользователя"""
        page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for page in page_names:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.context['page_obj'][0], self.post)

    def test_post_is_not_available_for_another_group(self):
        """Создав пост (см `setUp`), не увидим его на странице группы,
        для которой он не был предназначен"""
        group2 = Group(slug='second_group')
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': group2.slug})
        )
        if 'page_obj' in response.context:
            self.assertNotEqual(response.context['page_obj'][0], self.post)

    def test_pages_show_correct_paginator(self):
        """Paginator для главной страницы, страницы групп и в профиле
        пользователя сформирован правильно."""
        def url(url, **kwargs):
            return reverse(url, kwargs=kwargs)

        Post.objects.bulk_create(
            Post(
                author=self.user,
                text=f'Номер созданного поста {i}',
                group=self.group
            )
            for i in range(1, LAST_POST_COUNT_13)
        )
        urls = [
            url('posts:index'),
            url('posts:group_list', slug=self.group.slug),
            url('posts:profile', username=self.post.author),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 POST_AMOUNT_10)
                response = self.guest_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 POST_AMOUNT_3)

    def test_post_index_page_contains_cache(self):
        cache_response = self.guest_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(cache_response.content, response.content)
        cache.clear()
        response = self.guest_client.get(reverse("posts:index"))
        self.assertNotEqual(cache_response.content, response.content)

