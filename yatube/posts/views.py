from django.shortcuts import render, get_object_or_404, redirect
from .models import Group, Post, User, Comment, Follow
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

num_page_paginator = 10


def paginator(request, posts):
    paginator = Paginator(posts, num_page_paginator)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.select_related('group')
    context = {
        'page_obj': paginator(request, posts)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.post.all()
    context = {
        'page_obj': paginator(request, posts),
        'group': group
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()

    following = Follow.objects.filter(author=author).exists()
    context = {'author': author,
               'page_obj': paginator(request, posts),
               'posts': posts,
               'following': following
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comment = Comment.objects.filter(post=post)
    context = {
        'posts': post,
        'form': form,
        'comments': comment
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post.id)

    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# posts/views.py

@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    context = {
        'posts': posts,
        'page_obj': paginator(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    # Подписаться на автора
    Follow.objects.create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    # Дизлайк, отписка
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username=username)
