from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100,primary_key=True, default='')
    user_email = models.EmailField(default='')
    password = models.CharField(max_length=128, default='')
    is_active = models.BooleanField(max_length=1, default=1)

class VideoPostura(models.Model):
    nome = models.CharField(max_length=255)
    video = models.FileField(upload_to='videos/', default='')
    data_upload = models.DateTimeField(auto_now_add=True)
    deitado = models.FloatField(default=0.0)
    sentado = models.FloatField(default=0.0)
    levantado = models.FloatField(default=0.0)

    def __str__(self):
        return self.nome
