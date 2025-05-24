from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VideoPostura
from django.core.validators import FileExtensionValidator

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # não mostra a senha na resposta

    class Meta:
        model = User
        fields = ['id', 'username', 'password']  # escolha os campos que quiser expor
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
class ModeloUploadSerializer(serializers.Serializer):
    arquivo = serializers.FileField()


class VideoPosturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPostura
        fields = '__all__'
        read_only_fields = ['nome', 'deitado', 'sentado', 'levantado', 'data_upload']
