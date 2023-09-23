from django.urls import path, include
from .views import LessonModelViewSet, ProductsViewSet, AllProductsViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'lessons', LessonModelViewSet)
router.register(r'products', ProductsViewSet)
router.register(r'all-products', AllProductsViewSet)


urlpatterns = [
    path('', include(router.urls)),
]



