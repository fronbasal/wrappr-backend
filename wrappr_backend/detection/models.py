import os
from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from wrappr_backend import settings
from wrappr_backend.detection.demo import get_classes, detect_image
from wrappr_backend.detection.model.yolo_model import YOLO
from wrappr_backend.detection.mixins import TimestampMixin, UUIDMixin

import cv2


def frame_path(instance, filename):
    return f"{instance.context.id}/{instance.id}.{filename.split('.')[-1]}"


def result_path(instance, filename):
    return f"{instance.frame.context.id}/{instance.id}.{filename.split('.')[-1]}"


class Context(TimestampMixin, UUIDMixin):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self): return f"{self.user} at {self.timestamp}"


class Frame(TimestampMixin, UUIDMixin):
    context = models.ForeignKey(Context, models.CASCADE)
    image = models.ImageField(upload_to=frame_path)

    def get_image(self): return self.image.url

    def get_user(self): return self.context.user


class Result(TimestampMixin, UUIDMixin):
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=result_path, null=True, blank=True)

    def get_image(self): return self.image.url

    def get_user(self): return self.frame.get_user()


class Object(UUIDMixin):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    label = models.CharField(max_length=255)
    confidence = models.CharField(max_length=255, blank=True, null=True)
    score = models.PositiveIntegerField(blank=True, null=True)

    def get_user(self): return self.result.get_user()

    def __str__(self): return f"{self.label} at {self.x1}, {self.y1}"


@receiver([post_save], sender=Frame)
def detect_objects(sender, instance, **kwargs):
    classes = get_classes(os.path.join(settings.BASE_DIR, "wrappr_backend/detection/data/coco_classes.txt"))
    image = cv2.imread(instance.image.path)
    image = detect_image(image, YOLO(0.6, 0.5), classes)
    img_temp = NamedTemporaryFile(delete=True)
    _, buf = cv2.imencode(".jpg", image)
    img_temp.write(buf)
    r = Result()
    r.image.save(f"{instance.id}.jpg", File(img_temp))
    r.frame = instance
    r.save()
