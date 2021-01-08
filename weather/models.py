from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    favorite = models.BooleanField(default=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.user.username}'
