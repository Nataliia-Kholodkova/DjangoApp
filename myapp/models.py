import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    emotions = models.TextField(max_length=1000, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, default='user_empty_photo.jpg')

    def set_image_to_default(self):
        os.remove(self.photo.path)
        self.photo = 'user_empty_photo.jpg'
        super(Profile, self).save()

    def __str__(self):
        return self.user.username


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, name='user', related_name='posts')
    title = models.CharField(max_length=200, default='', blank=True, null=True)
    text = models.TextField(max_length=30000)
    created_date = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, name='post', related_name='images')
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        os.remove(self.image.path)
        super().delete(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, name='user', related_name='comments', default=None)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, name='post', related_name='comments', default=None)
    text = models.TextField(max_length=3000)
    created_date = models.DateTimeField(default=timezone.now)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
