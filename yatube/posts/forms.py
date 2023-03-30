from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Изображение, которое будет относиться к посту',
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        help_text = {
            'text': 'Текст нового комментария',
        }
        labels = {
            'text': 'Текст комментария',
        }
