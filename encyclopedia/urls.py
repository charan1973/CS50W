from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("error", views.error, name="error"),
    path("search", views.search, name="search"),
    path("save", views.save, name="save"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random", views.random_page, name="random")
]
