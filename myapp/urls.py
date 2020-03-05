from django.urls import path

from . import views

app_name = 'myapp'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('account/edit', views.edit_account, name='edit_account'),
    path('account/add_post', views.add_post, name='add_post'),
    path('show_post/<int:id>', views.show_post, name='show_post'),
    path('account/edit_post/<int:id>', views.edit_post, name='edit_post'),
    path('account/delete_photo/<int:id>', views.delete_photo, name='delete_photo'),
    path('account/delete_image/<int:post_id>/<int:img_id>', views.delete_image, name='delete_image'),
    path('account/delete_post/<int:id>', views.delete_post, name='delete_post'),
    path('search', views.search, name='search'),
    path('dislike/<int:post_id>', views.dislike_post, name='dislike_post'),
    path('like/<int:post_id>', views.like_post, name='like_post'),

]
