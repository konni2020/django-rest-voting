from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from accounts.serializers import UserSerializer


def get_token(request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return user.auth_token.key


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        response = super().post(request)
        token = get_token(request)
        if token:
            response.data['token'] = token
        return response


class LoginView(APIView):
    permission_classes = ()

    def post(self, request):
        token = get_token(request)
        if token:
            return Response({'token': token})
        else:
            return Response(
                {'error': 'Wrong Credentials'},
                status=status.HTTP_400_BAD_REQUEST)
