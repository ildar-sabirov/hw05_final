from django.contrib import admin
from .models import Post, Group, Follow, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'text', 'created', 'author')
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Follow)
admin.site.register(Comment, CommentAdmin)
