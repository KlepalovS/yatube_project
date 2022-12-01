from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/rating_up/', views.rating_up, name='rating_up'),
    path('posts/<int:post_id>/rating_down/', views.rating_down, name='rating_down'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path('create/', views.post_create, name='post_create'),
]
