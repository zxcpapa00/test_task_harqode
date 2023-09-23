from rest_framework import serializers
from products import models


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Lesson
        exclude = ('viewers', )


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    lesson = LessonSerializer(many=True)

    class Meta:
        model = models.Product
        fields = ('id', 'owner', 'lesson')




