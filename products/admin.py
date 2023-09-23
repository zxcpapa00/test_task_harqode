from django.contrib import admin
from .models import Product, Lesson, LessonViewer, Access

admin.site.register(Product)
admin.site.register(Lesson)
admin.site.register(LessonViewer)
admin.site.register(Access)
