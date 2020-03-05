from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

from .models import Profile, Post, Comment, Image


class CreateUser(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CreateUser, self).save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class EditUser(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('city', 'gender', 'emotions', 'photo')


class AddPost(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
        )


class ListingFormImage(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)


class EditPost(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text'
        )


class AddComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
