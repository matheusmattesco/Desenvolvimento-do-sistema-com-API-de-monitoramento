from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import get_object_or_404

import os

from .models import VideoPostura 
from .serializers import UserSerializer, ModeloUploadSerializer, VideoPosturaSerializer
from .posture_detection import analisar_posturas


# === USUÁRIOS ===

@swagger_auto_schema(method='get', operation_summary="Listar usuários")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserSerializer, operation_summary="Registrar novo usuário")
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('user', openapi.IN_QUERY, description="Username do usuário", type=openapi.TYPE_STRING)
    ],
    operation_summary="Obter dados de um usuário autenticado"
)
@swagger_auto_schema(method='put', request_body=UserSerializer, operation_summary="Atualizar usuário")
@swagger_auto_schema(
    method='delete',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username do usuário a ser deletado')
        },
        required=['username']
    ),
    operation_summary="Deletar usuário",
    operation_description="Deleta um usuário com base no campo 'username'. Requer autenticação."
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_manager(request):
    if request.method == 'GET':
        username = request.GET.get('user')
        if not username:
            return Response({'error': 'Parâmetro "user" é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response({'mensagem': 'Usuário deletado com sucesso'}, status=status.HTTP_202_ACCEPTED)


# === UPLOAD MODELO ===

@swagger_auto_schema(
    method='post',
    request_body=ModeloUploadSerializer,
    operation_summary="Upload do modelo treinado",
    operation_description="Faz upload de um modelo (.pkl ou .pt) e o salva como modelo ativo para classificações."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_modelo(request):
    arquivo = request.FILES.get('arquivo')
    if not arquivo:
        return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

    caminho_dir = os.path.join(settings.MEDIA_ROOT, 'modelo')
    os.makedirs(caminho_dir, exist_ok=True)

    caminho_arquivo = os.path.join(caminho_dir, 'modelo_ativo.pkl')
    with open(caminho_arquivo, 'wb+') as destino:
        for chunk in arquivo.chunks():
            destino.write(chunk)

    return Response({"mensagem": "Modelo salvo com sucesso!"}, status=status.HTTP_200_OK)


# === UPLOAD VÍDEO ===

@swagger_auto_schema(
    method='post',
    request_body=VideoPosturaSerializer,
    operation_summary="Upload de vídeo para reconhecimento de postura",
    operation_description="Faz upload do vídeo e salva o nome do arquivo no banco."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_video(request):
    serializer = VideoPosturaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    video_instance = serializer.save()
    video_path = video_instance.video.path
    resultado_analise = analisar_posturas(video_path)

    mapa_posturas = {
        "Sentado": "sentado",
        "Levantado": "levantado",
        "Deitado": "deitado",
    }

    for postura, duracao in resultado_analise.items():
        campo = mapa_posturas.get(postura)
        if campo and hasattr(video_instance, campo):
            setattr(video_instance, campo, duracao)

    video_instance.save()

    return Response({
        "video": VideoPosturaSerializer(video_instance).data,
        "analise": resultado_analise
    })


# === LISTAR RESULTADOS ===

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_todos_resultados(request):
    videos = VideoPostura.objects.all()
    resultados = []

    for video in videos:
        resultados.append({
            "id": video.id,
            "nome": video.nome,
            "deitado": video.deitado,
            "sentado": video.sentado,
            "levantado": video.levantado,
            "video_url": request.build_absolute_uri(video.video.url)
        })

    return Response(resultados, status=status.HTTP_200_OK)
