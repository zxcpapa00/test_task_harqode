from django.db import models
from django.contrib.auth.models import User
from moviepy.editor import VideoFileClip


class Lesson(models.Model):
    name = models.CharField(max_length=255)
    video_link = models.CharField(max_length=2048)
    duration = models.IntegerField(default=0)
    viewers = models.ManyToManyField(User, through='LessonViewer')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        self.set_duration()

    def set_duration(self):
        try:
            clip = VideoFileClip(self.video_link)
            self.duration = int(clip.duration)
            self.save_base()
            clip.close()
        except Exception as ex:
            print('Ошибка видеофайла')


class LessonViewer(models.Model):
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

    def check_viewed(self):
        if self.view_time >= self.lesson.duration * 0.8:
            self.viewed = self.VIEWED
            self.save_base()


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ManyToManyField(Lesson, related_name='lessons')

    def __str__(self):
        return f'{self.owner} product'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        for us in self.access.all():
            user = us.user
            for lesson in self.lesson.all():
                viewer = LessonViewer.objects.get(user=user, lesson=lesson)
                if not viewer:
                    LessonViewer.objects.create(user=user, lesson=lesson)


class Access(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='access')

    def __str__(self):
        return f'{self.user} have access for {self.product}'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
        for lesson in self.product.lesson.all():
            LessonViewer.objects.create(user=self.user, lesson=lesson)
