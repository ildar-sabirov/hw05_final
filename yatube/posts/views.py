from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from .serializers import PostSerializer
from django.http import JsonResponse


def paginator(request, posts, select_limit):
    paginator = Paginator(posts, select_limit)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    page_obj = paginator(request, post_list, 10)
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.all().select_related('author')
    page_obj = paginator(request, post_list, 10)
    template = 'posts/group_list.html'
    title = f'Записи сообщества {group}'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().select_related('group')
    page_obj = paginator(request, posts, 10)
    count = posts.count()
    follower_counts = Follow.objects.filter(author=user).count()
    flag = user != request.user
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user
        ).exists()
    else:
        following = False
    context = {
        'author': user,
        'username': username,
        'count': count,
        'page_obj': page_obj,
        'following': following,
        'not_the_current_user': flag,
        'follower_counts': follower_counts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts = Post.objects.filter(author=post.author)
    count = posts.count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post_id': post_id,
        'post': post,
        'count': count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user.username)
    else:
        form = PostForm()

    title = 'Новый пост'
    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    title = 'Редактирование поста'
    context = {
        'is_edit': True,
        'title': title,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    page_obj = paginator(request, posts, 10)

    context = {
        'title': 'Подписки на авторов',
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)


def get_post(request, pk):
    if request.method == 'GET':
        post = get_object_or_404(Post, id=pk)
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data)
