from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, PostRating, User
from .utils import get_posts_paginator


@cache_page(settings.CACHES_TIMEOUT_INDEX_PAGE, key_prefix='index_page')
def index(request):
    """Стартовая страница, выводим все посты из БД."""
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = get_posts_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Выводим посты в группе."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_in_group.all()
    page_obj = get_posts_paginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Выводим профиль автора."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.author_of_posts.all()
    page_obj = get_posts_paginator(posts, request)
    following = (
        request.user.is_authenticated and request.user.follower.filter(
            author=author,
        ).exists()
    )
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Выводим информацию о посте."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.post_comments.all()
    rating = post.rating_post.all()
    is_rating = (
        request.user.is_authenticated and request.user.rating_user.filter(
            post=post,
        ).exists()
    )
    print(is_rating)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'rating': rating,
        'form': form,
        'is_rating': is_rating,
    }
    return render(request, template, context)


@login_required()
def rating_up(request, post_id):
    """Увеличиваем рейтинг комментария к посту."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        PostRating.objects.get_or_create(
            post=post,
            user=request.user,
        )
    return redirect('posts:post_detail', post_id)

@login_required()
def rating_down(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        PostRating.objects.filter(
            post=post,
            user=request.user,
        ).delete()
    return redirect('posts:post_detail', post_id)


@login_required()
def post_create(request):
    """Создаем новый пост."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        form.save()
        return redirect('posts:profile', new_post.author)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required()
def post_edit(request, post_id):
    """Редактируем созданный пост."""
    template = 'posts/create_post.html'
    editable_post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=editable_post,
    )
    context = {
        'form': form,
        'is_edit': True,
    }
    if request.user != editable_post.author:
        return redirect('posts:post_detail', editable_post.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', editable_post.pk)
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Создаем комментарии к посту."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.post_comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    """Выводим посты авторов, на которых подписались."""
    template = 'posts/follow.html'
    follow_count = Follow.objects.filter(user=request.user).count()
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_posts_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'follow': True,
        'follow_count': follow_count,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписываемся на профиль автора."""
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    """Отписываемся от профиля автора."""
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', author.username)
