from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
