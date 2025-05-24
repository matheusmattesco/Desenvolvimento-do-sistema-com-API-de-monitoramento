from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100,primary_key=True, default='')
    user_email = models.EmailField(default='')
    password = models.CharField(max_length=128, default='')
    is_active = models.BooleanField(max_length=1, default=1)


    def __str__(self):
        return f'Nickname: {self.user_nickname} | E-mail: {self.user_email}'
