# users/views.py
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Favorite, User
from .serializers import FavoriteSerializer, UserLoginSerializer, UserRegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "message": "注册成功",
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"message": "注册失败", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as e:
            return Response(
                {"message": "用户名或邮箱已存在", "errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "注册失败", "errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):
    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data["username"]
                password = serializer.validated_data["password"]
                user = authenticate(username=username, password=password)

                if user:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "message": "登录成功",
                            "token": {
                                "refresh": str(refresh),
                                "access": str(refresh.access_token),
                            },
                        }
                    )
                return Response(
                    {"message": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {"message": "登录失败", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "登录失败", "errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def favorite_view(request):
    if request.method == "GET":
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        symbol = request.data.get("symbol")
        if not symbol:
            return Response(
                {"error": "Symbol is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        favorite, created = Favorite.objects.get_or_create(
            user=request.user, symbol=symbol
        )
        return Response(
            {"status": "success"},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    elif request.method == "DELETE":
        symbol = request.data.get("symbol")
        if not symbol:
            return Response(
                {"error": "Symbol is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            favorite = Favorite.objects.get(user=request.user, symbol=symbol)
            favorite.delete()
            return Response({"status": "success"})
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({"username": user.username, "email": user.email})


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    data = request.data

    if "username" in data:
        # 检查用户名是否已存在
        if User.objects.filter(username=data["username"]).exclude(id=user.id).exists():
            return Response({"message": "用户名已存在"}, status=400)
        user.username = data["username"]

    if "email" in data:
        # 检查邮箱是否已存在
        if User.objects.filter(email=data["email"]).exclude(id=user.id).exists():
            return Response({"message": "邮箱已存在"}, status=400)
        user.email = data["email"]

    user.save()
    return Response(
        {"username": user.username, "email": user.email, "message": "更新成功"}
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        user = request.user
        user.delete()
        return Response({"message": "账号已成功删除"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": "删除账号失败", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
