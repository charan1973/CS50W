from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "created_by", "created_at")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)