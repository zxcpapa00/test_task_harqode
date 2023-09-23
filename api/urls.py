from django.urls import path, include
from .views import LessonModelViewSet, ProductsViewSet, AllProductsViewSet
from rest_framework import routers

router = routers.DefaultRouter()
# Вывод всех уроков по всем продуктам к которым пользователь имеет доступ
router.register(r'lessons', LessonModelViewSet)

# Вывод уроков по конкретному продукту по пути /products/<int:pk>
router.register(r'products', ProductsViewSet)

# Вывод всех продуктов с подробной информацией
router.register(r'all-products', AllProductsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]



