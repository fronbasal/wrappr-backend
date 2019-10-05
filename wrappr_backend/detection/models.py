from django.contrib.auth import get_user_model
from django.db import models

from wrappr_backend.detection.mixins import TimestampMixin, UUIDMixin


def frame_path(instance, filename):
    return f"{instance.context.uuid}/{instance.uuid}.{filename.split('.')[-1]}"


def result_path(instance, filename):
    return f"{instance.frame.context.uuid}/{instance.uuid}.{filename.split('.')[-1]}"


class Context(TimestampMixin, UUIDMixin):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class Frame(TimestampMixin, UUIDMixin):
    context = models.ForeignKey(Context, models.CASCADE)
    height = models.IntegerField()
    width = models.IntegerField()
    image = models.ImageField(height_field="height", width_field="width", upload_to=frame_path)


class Result(TimestampMixin, UUIDMixin):
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=result_path)
    score = models.IntegerField()


class Object(UUIDMixin):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=True)
