from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, symmetrical=False)

    # To get following use user.following.all()
    #To get followers use User.objects.all(following=user)

class Post(models.Model):
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=CASCADE, related_name="post")
    like = models.ManyToManyField(User, blank=True, related_name="liked")

    class Meta:
        ordering = ['-created_at']