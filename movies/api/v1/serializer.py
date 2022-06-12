from rest_framework import serializers

from movies.models import Filmwork


class FilmworkSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    actors = serializers.SlugRelatedField(many=True, read_only=True, slug_field='full_name')
    directors = serializers.SlugRelatedField(many=True, read_only=True, slug_field='full_name')
    writers = serializers.SlugRelatedField(many=True, read_only=True, slug_field='full_name')

    class Meta:
        model = Filmwork
        fields = ('id', 'title', 'description', 'creation_date', 'rating', 'type',
                  'genres', 'actors', 'directors', 'writers')
