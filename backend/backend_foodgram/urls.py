from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet

v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(v1_router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
