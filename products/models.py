from django.db import models
from django.contrib.auth.models import User
from moviepy.editor import VideoFileClip


class Lesson(models.Model):
    """Модель урока"""
    name = models.CharField(max_length=255)
    video_link = models.CharField(max_length=2048)
    duration = models.IntegerField(default=0)
    viewers = models.ManyToManyField(User, through='LessonViewer')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        # Функция вызывается для автоматического проставления поля duration
        self.set_duration()

    # Функция для добавления продолжительности видео
    def set_duration(self):
        try:
            clip = VideoFileClip(self.video_link)
            self.duration = int(clip.duration)
            self.save_base()
            clip.close()
        except Exception as ex:
            print('Ошибка видеофайла')


class LessonViewer(models.Model):
    """Модель студента для урока с доп. информацией"""
    VIEWED = 'Просмотрено'
    NOT_VIEWED = 'Не просмотрено'
    STATUSES = (
        (NOT_VIEWED, 'Не просмотрено'),
        (VIEWED, 'Просмотрено'),
    )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view_time = models.IntegerField(default=0)
    viewed = models.CharField(max_length=20, choices=STATUSES, default=NOT_VIEWED)

    def __str__(self):
        return f'{self.user} view {self.lesson} {self.view_time}'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        self.check_viewed()

    # Функция для проверки времени просмотра ролика
    def check_viewed(self):
        if self.view_time >= self.lesson.duration * 0.8:
            self.viewed = self.VIEWED
            self.save_base()


class Product(models.Model):
    """Модель продукта"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ManyToManyField(Lesson, related_name='lessons')

    def __str__(self):
        return f'{self.owner} product'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

        # Проходим по всем студентам у которых есть доступ
        for us in self.access.all():
            user = us.user
            # Проходим по всем урока на продукте
            for lesson in self.lesson.all():
                # Получаем студента урока
                viewer = LessonViewer.objects.get(user=user, lesson=lesson)
                # Если его нет, то создаем
                if not viewer:
                    LessonViewer.objects.create(user=user, lesson=lesson)


class Access(models.Model):
    """Модель доступа студента к продукту"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='access')

    def __str__(self):
        return f'{self.user} have access for {self.product}'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        # При получении доступа к уроку, создаем модели студента
        for lesson in self.product.lesson.all():
            LessonViewer.objects.create(user=self.user, lesson=lesson)
