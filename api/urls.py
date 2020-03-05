from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path('token/get/', TokenObtainPairView.as_view(), name='token_get'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('posts/own/', views.user_posts, name='own_posts'),
    path('posts/', views.posts, name='posts'),
    path('login/', views.LogInView.as_view(), name='api_login'),
    path('register/', views.register, name='api_register'),
    path('posts/add/', views.add_post, name='add_post'),
    path('posts/delete/<int:id>/', views.delete_post, name='delete_post'),
    path('posts/like/<int:id>/', views.like_post, name='like_post'),
    path('posts/dislike/<int:id>/', views.dislike_post, name='dislike_post'),
    path('posts/comments/get/<int:id>/', views.get_comments, name='get_comments'),
    path('posts/comments/add/<int:id>/', views.add_comment, name='add_comment')
]
