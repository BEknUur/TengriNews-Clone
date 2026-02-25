from django.shortcuts import render
from rest_framework import viewsets, permissions
from apps.accounts.models import CustomUser
from apps.accounts.serializers import UserSerializer, UserUpdateSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.IsAdminUser()]
        if self.action in ("me", "partial_update_me"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"], url_path="me", url_name="me")
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="me", url_name="partial_update_me")
    def partial_update_me(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)