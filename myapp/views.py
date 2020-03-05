from PIL import Image as Img
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse

from .forms import CreateUser, EditUser, EditProfile, AddComment, AddPost, EditPost
from .models import Profile, Post, Image, Comment


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'You are logged in as {}'.format(username))
                return redirect('myapp:account')
            else:
                messages.error(request, 'Username or password is invalid')
        else:
            for message in form.error_messages:
                messages.error(request, '{}: {}'.format(message, form.error_messages[message]))
    form = AuthenticationForm
    return render(request, 'myapp/login.html', {'form': form})


def photo_resize(inst):
    image = Img.open(inst.photo)
    size = (300, 300)
    image.resize(size, Img.ANTIALIAS)
    image.save(inst.photo.path)
    inst.save()


def image_resize(inst):
    image = Img.open(inst.image)
    size = (300, 300)
    image.resize(size, Img.ANTIALIAS)
    image.save(inst.image.path)
    inst.save()


def home(request):
    posts = Post.objects.all().order_by('created_date')
    return render(request, 'myapp/home.html', {'posts': posts})


def logout_user(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('myapp:home')


def register(request):
    form = CreateUser(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            users = User.objects.filter(username=form.data['username']).all()
            if users:
                messages.error(request, 'Usernsme already exists')
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'New account created: {}'.format(username))
            login(request, user)
            return redirect('myapp:edit_account')
        else:
            for message in form.error_messages:
                messages.error(request, '{}: {}'.format(message, form.error_messages[message]))
    return render(request=request,
                  template_name='myapp/register.html',
                  context={'form': form})


@login_required(login_url='/login')
def account(request):
    user = request.user
    posts = Post.objects.filter(user=user).all()
    return render(request, 'myapp/account.html', context={'user': user, 'posts': posts})


@login_required(login_url='/login')
def edit_account(request):
    form_user = EditUser(instance=request.user, data=request.POST or None)
    form_profile = EditProfile(instance=request.user.profile, files=request.FILES, data=request.POST or None)
    if form_user.is_valid() and form_profile.is_valid():
        if 'user_empty_photo' in form_profile.cleaned_data.get('photo'):
            form_profile.cleaned_data.pop('photo')
        form_user.save()
        profile = form_profile.save()
        if 'user_empty_photo' not in profile.photo.path:
            photo_resize(profile)
        messages.success(request, 'Information changed successfully')
        return redirect('myapp:account')
    return render(request=request,
                  template_name='myapp/edit_account.html',
                  context={'form_user': form_user, 'form_profile': form_profile})


@login_required(login_url='/login')
def add_post(request):
    form = AddPost(data=request.POST or None)
    if form.is_valid():
        post = Post(user=request.user, title=form.cleaned_data.get('title'), text=form.cleaned_data.get('text'))
        post.save()
        for file in request.FILES.getlist('images'):
            instance = Image(
                post=post,
                image=file
            )
            instance.save()
            image_resize(instance)
        return redirect('myapp:account')
    return render(request=request,
                  template_name='myapp/add_post.html',
                  context={'form': form})


@login_required(login_url='/login')
def edit_post(request, id):
    post = Post.objects.filter(user=request.user, pk=id).get()
    form = EditPost(instance=post, data=request.POST or None)
    if form.is_valid():
        form.save()
        for file in request.FILES.getlist('images'):
            instance = Image(
                post=post,
                image=file
            )
            instance.save()
            image_resize(instance)
            instance.save()
        return redirect('myapp:show_post', id=id)
    return render(request=request,
                  template_name='myapp/edit_post.html',
                  context={'form': form, 'post': post})


def show_post(request, id):
    user = request.user
    post = Post.objects.filter(pk=id).get()
    images = post.images.all()
    comments = Comment.objects.filter(post=post).all()
    form = AddComment(data=request.POST or None)
    if form.is_valid() and request.user.is_authenticated:
        comment = Comment(
            user=request.user,
            text=form.cleaned_data["text"],
            post=post
        )
        comment.save()
        return redirect(reverse('myapp:show_post', args=(post.pk,)))
    return render(request, 'myapp/show_post.html', context={'user': user, 'post': post, 'images': images,
                                                            'comments': comments, 'form': form})


@login_required(login_url='/login')
def delete_image(request, post_id, img_id):
    Image.objects.get(pk=img_id).delete()
    return redirect('myapp:edit_post', id=post_id)


@login_required(login_url='/login')
def delete_photo(request, id):
    profile = Profile.objects.get(pk=id)
    profile.set_image_to_default()

    return redirect('myapp:edit_account')


@login_required(login_url='/login')
def delete_post(request, id):
    post = Post.objects.get(pk=id)
    post.delete(keep_parents=True)
    return redirect('myapp:account')


@login_required(login_url='/login')
def like_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if not request.user.is_authenticated:
        messages.error(request, 'Cannot score this post. Log in first!')
        return redirect(reverse('myapp:show_post', args=(post.pk,)))

    post.likes += 1
    post.save()
    return redirect(reverse('myapp:show_post', args=(post.pk,)))


@login_required(login_url='/login')
def dislike_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if not request.user.is_authenticated:
        messages.error(request, 'Cannot score this post. Log in first!')
        return redirect(reverse('myapp:show_post', args=(post.pk,)))

    post.dislikes += 1
    post.save()
    return redirect(reverse('myapp:show_post', args=(post.pk,)))


def search(request):
    posts = Post.objects.all()
    query = request.GET['search'].lower()
    results = [post for post in posts if query in post.text.lower() or query in post.title.lower()]
    return render(request, 'myapp/post_template.html', context={'posts': results})
