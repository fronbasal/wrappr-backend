from django.contrib.auth import get_user_model
from django.db import models

from wrappr_backend.detection.mixins import TimestampMixin, UUIDMixin


def frame_path(instance, filename):
    return f"{instance.context.id}/{instance.id}.{filename.split('.')[-1]}"


def result_path(instance, filename):
    return f"{instance.frame.context.id}/{instance.id}.{filename.split('.')[-1]}"


class Context(TimestampMixin, UUIDMixin):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self): return f"{self.user} at {self.timestamp}"


class Frame(TimestampMixin, UUIDMixin):
    context = models.ForeignKey(Context, models.CASCADE)
    height = models.IntegerField()
    width = models.IntegerField()
    image = models.ImageField(height_field="height", width_field="width", upload_to=frame_path)

    def get_image(self): return self.image.url

    def get_user(self): return self.context.user


class Result(TimestampMixin, UUIDMixin):
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=result_path)

    def get_image(self): return self.image.url

    def get_user(self): return self.frame.get_user()


class Object(UUIDMixin):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    label = models.CharField(max_length=255, blank=True)
    confidence = models.CharField(max_length=255, blank=True)
    score = models.PositiveIntegerField()

    def get_user(self): return self.result.get_user()
