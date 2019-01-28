from rest_framework import generics, status, viewsets

from accounts.serializers import UserSerializer


class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer