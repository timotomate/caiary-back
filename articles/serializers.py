from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'emotion', 'location', 'menu', 'weather', 'song', 'point', 'content', 'image', 'user', 'created', 'liked']

    def get_image(self, article):
        request = self.context.get('request')

        if article.image:
            image = article.image.url
            image_url = request.build_absolute_uri(image)

            return image_url

        return None

