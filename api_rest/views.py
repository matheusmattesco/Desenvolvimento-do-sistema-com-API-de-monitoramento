from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import VideoPostura 
from .serializers import UserSerializer, ModeloUploadSerializer, VideoPosturaSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .posture_detection import analisar_posturas


@swagger_auto_schema(
    method='get',
    operation_summary="Listar usuários",
    operation_description="Retorna todos os usuários cadastrados no sistema."
)
@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_summary="Buscar usuário por nickname",
    operation_description="Retorna os dados de um usuário com base no seu nickname (pk)."
)
@api_view(['GET'])
def get_by_nick(request, nick):
    try:
        user = User.objects.get(pk=nick)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    operation_summary="Registrar novo usuário",
    operation_description="Cria um novo usuário com os dados fornecidos."
)
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
    operation_summary="Obter dados de um usuário autenticado",
    operation_description="Retorna os dados de um usuário com base no parâmetro `user`, se autenticado."
)
@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    operation_summary="Atualizar usuário",
    operation_description="Atualiza os dados de um usuário existente. Requer autenticação."
)
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
        try:
            if request.GET['user']:
                username = request.GET['user']
                try:
                    user = User.objects.get(pk=username)
                except:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        nickname = request.data['username']
        updated_user = User.objects.get(pk=nickname)
        serializer = UserSerializer(updated_user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            user_to_delete = User.objects.get(pk=request.data['username'])
            user_to_delete.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    manual_parameters=[],
    request_body=ModeloUploadSerializer,
    operation_summary="Upload do modelo treinado",
    operation_description="Faz upload de um modelo (.pkl ou .pt) e o salva como modelo ativo para classificações."
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_modelo(request):
    arquivo = request.FILES.get('arquivo')
    if not arquivo:
        return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)
    
    media_path = settings.MEDIA_ROOT
    if not os.path.exists(media_path):
        os.makedirs(media_path)

    caminho = os.path.join(media_path, 'modelo/modelo_ativo.pkl')

    with open(caminho, 'wb+') as destino:
        for chunk in arquivo.chunks():
            destino.write(chunk)

    return Response({"mensagem": "Modelo salvo com sucesso!"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=VideoPosturaSerializer,
    operation_summary="Upload de vídeo para reconhecimento de postura",
    operation_description="Faz upload do vídeo e salva o nome do arquivo no banco."
)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_video(request):
    serializer = VideoPosturaSerializer(data=request.data)
    if serializer.is_valid():
        video_instance = serializer.save() 

        video_file_path = video_instance.video.path
        resultado_analise = analisar_posturas(video_file_path)


        mapa_posturas = {
            "Sentado": "sentado",
            "Levantado": "levantado",
            "Deitado": "deitado",
        }

        for postura, duracao in resultado_analise.items():
            campo_modelo = mapa_posturas.get(postura)
            if campo_modelo and hasattr(video_instance, campo_modelo):
                setattr(video_instance, campo_modelo, duracao)

        video_instance.save()

        serializer = VideoPosturaSerializer(video_instance)
        return Response({
            "video": serializer.data,
            "analise": resultado_analise
        })


    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny]) 
def listar_todos_resultados(request):
    videos = VideoPostura.objects.all()
    serializer = VideoPosturaSerializer(videos, many=True)

    print("teste")

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