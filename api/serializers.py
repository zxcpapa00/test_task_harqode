from rest_framework import serializers
from products import models


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока"""

    class Meta:
        model = models.Lesson
        exclude = ('viewers', )


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продукта"""
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    lesson = LessonSerializer(many=True)

    class Meta:
        model = models.Product
        fields = ('id', 'owner', 'lesson')




