from django.test import TestCase

from ..models import Group, Post


class PostModelTest(TestCase):
    def test_str_returns_correct_string_representation(self):
        """Метод __str__ возвращает удобочитаемое
        строковое представление объекта."""
        post = Post(text='Короткий пост')
        self.assertEqual('Короткий пост', str(post))

        long_post = Post(text='Не более 15 символов может уместиться в превью')
        self.assertEqual('Не более 15 сим', str(long_post))

        group = Group(title='Название группы')
        self.assertEqual('Название группы', str(group))

    def test_verbose_name_fields_match_the_expected_text(self):
        def hint(field):
            return Post._meta.get_field(field).verbose_name

        self.assertEqual(hint('text'), 'Текст поста')
        self.assertEqual(hint('group'), 'Группа')
        self.assertEqual(hint('pub_date'), 'Дата публикации')
        self.assertEqual(hint('author'), 'Автор')

    def test_help_text_fields_match_the_expected_text(self):
        def hint(field):
            return Post._meta.get_field(field).help_text

        self.assertEqual(hint('text'), 'Введите текст поста')
        self.assertEqual(hint('group'),
                         'Группа, к которой будет относиться пост')
