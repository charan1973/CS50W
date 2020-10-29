
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_post", views.add_post, name="add_post"),
    path("like_post", views.like_post, name="like_post"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("following", views.following, name="following"),
    path("follow", views.follow, name="follow")
]
