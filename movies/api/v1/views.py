from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from movies.api.v1 import serializer
from movies.api.v1.paginators import SimplePageNumberPaginator
from movies.models import Filmwork


class FilmworkViewSet(ModelViewSet):
    queryset = Filmwork.objects.all()
    serializer_class = serializer.FilmworkSerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]
    pagination_class = SimplePageNumberPaginator

    def get_queryset(self):
        qs = super().get_queryset().order_by('id').prefetch_related('genres')
        qs = Filmwork.prefetch_roles(qs)
        return qs
