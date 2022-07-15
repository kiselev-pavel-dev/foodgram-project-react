from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import User
from .serializers import UserSerializerList


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
