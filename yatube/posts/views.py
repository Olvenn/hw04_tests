from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.constants import POSTS_PER_STR

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import create_page_object


def index(request):
    post_list = Post.objects.all()
    page_obj = create_page_object(request, post_list, POSTS_PER_STR)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.select_related('group')
    page_obj = create_page_object(request, posts, POSTS_PER_STR)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('author')
    posts_count = Post.objects.filter(author__exact=user).count
    page_obj = create_page_object(request, posts, POSTS_PER_STR)
    following = True
    # if request.user.is_authenticated  and user != request.user:
    #     following = Follow.objects.filter(user=request.user).exists()

    context = {
        "username": username,
        "author": user,
        "posts_count": posts_count,
        "page_obj": page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author__exact=post.author).count
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "posts_count": posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST, files=request.FILES or None)
    context = {
        'form': form,
    }

    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    # form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    if form.is_valid():
        post = form.save()
        form.instance.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, "posts/create_post.html", context)


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
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = create_page_object(request, posts, POSTS_PER_STR)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author)
    if request.user != author and not follow.exists():
        Follow.objects.create(user=request.user,
                              author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', username=username)
