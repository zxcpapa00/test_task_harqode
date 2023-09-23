from django.utils.timezone import now
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.models import Lesson, Product, LessonViewer, Access
from .serializers import LessonSerializer, ProductSerializer
from django.contrib.auth.models import User


class LessonModelViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        # Вывод уроков для конкретного пользователя
        queryset = Lesson.objects.filter(lessons__access__user=user)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Добавление дополнительной информации по уроку
        for lesson in serializer.data:
            lesson['user'] = str(LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).user)
            lesson['time_view'] = int(
                LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).view_time)
            lesson['status'] = str(LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).viewed)

        return Response(serializer.data)


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        # Вывод всех продуктов к которым пользователь имеет доступ
        return self.queryset.filter(access__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Добавление дополнительной информации по урокам продукта для конкретного пользователя
        for product in serializer.data:
            for lesson in product['lesson']:
                lesson['user'] = self.request.user.username
                lesson['view_time'] = LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).view_time
                lesson['status'] = str(LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).viewed)
                lesson['last_viewed'] = now().date()

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.queryset.get(id=kwargs['pk'])
        serializer = self.get_serializer(queryset)
        # Добавление дополнительной информации по урокам для конкретного продукта по его id
        for lesson in serializer.data['lesson']:
            lesson['user'] = self.request.user.username
            lesson['view_time'] = LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).view_time
            lesson['status'] = str(LessonViewer.objects.get(user=self.request.user, lesson_id=lesson['id']).viewed)
            lesson['last_viewed'] = now().date()
        return Response(serializer.data)


class AllProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Вывод всех продуктов на платформе с дополнительной информацией
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        sum_time = 0
        total_viewed = 0
        for product in serializer.data:
            for lesson in product['lesson']:
                total_viewed = LessonViewer.objects.filter(viewed='Просмотрено', lesson_id=lesson['id']).count()
                sum_time = sum(list(i.view_time for i in LessonViewer.objects.filter(lesson_id=lesson['id'])))
            product['total_viewed'] = total_viewed
            product['total_viewed_time'] = sum_time
            product['total_students'] = Access.objects.filter(product_id=product['id']).count()
            product['demand'] = float((product['total_students'] / User.objects.all().count()) * 100)
        return Response(serializer.data)
