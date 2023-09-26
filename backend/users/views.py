from api.paginations import LimitPagination
from api.serializers.users import FollowSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow, User


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly(),)
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.actuon == 'me':
            self.permission_classes = (IsAuthenticated)
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'],
            detail=True,)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=user, author=author
        )

        if request.methdo == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)

            if user == author:
                return Response({'error': 'Невозможно подписатсья на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscription(self, requset):
        user = requset.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            page, many=True,
            context={'requset': requset}
        )
        return self.get_paginated_response(serializer.data)
