from django.urls import include, path
from rest_framework import routers

from movies.api.v1 import views

router = routers.DefaultRouter()
router.register(r'movies', views.FilmworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
