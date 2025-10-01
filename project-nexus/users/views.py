from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import RegisterUserSerializer, LoginSerializer
from users.utils import get_auth_response 

class RegisterUserAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(get_auth_response(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(get_auth_response(user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"})
        except Exception as e:
            return Response({"message": "Successfully logged out"})


def user_profile(request, user_id):
    cache_key = f"user_profile_{user_id}"
    profile = cache.get(cache_key)

    if not profile:
        profile = get_object_or_404(User, pk=user_id)
        profile = {"id": profile.id, "username": profile.user.username, "email": profile.user.email}
        cache.set(cache_key, profile, timeout=60*10)  # Cache 10 mins

    return JsonResponse(profile)
