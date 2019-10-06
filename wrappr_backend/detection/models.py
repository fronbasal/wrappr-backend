from tempfile import TemporaryFile, NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from wrappr_backend import settings
from wrappr_backend.detection.mixins import TimestampMixin, UUIDMixin

import cv2
from keras.models import load_model
import numpy as np

from .utils.datasets import get_labels
from .utils.inference import detect_faces
from .utils.inference import draw_text
from .utils.inference import draw_bounding_box
from .utils.inference import apply_offsets
from .utils.inference import load_detection_model
from .utils.inference import load_image
from .utils.preprocessor import preprocess_input


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
def detect_emotion(sender, instance, **kwargs):
    image_path = instance.image.path
    detection_model_path = settings.DETECTION_MODEL
    emotion_model_path = settings.EMOTION_MODEL
    emotion_labels = get_labels('fer2013')
    font = cv2.FONT_HERSHEY_SIMPLEX

    # hyper-parameters for bounding boxes shape
    emotion_offsets = (20, 40)
    emotion_offsets = (0, 0)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    # loading images
    rgb_image = load_image(image_path, grayscale=False)
    gray_image = load_image(image_path, grayscale=True)
    gray_image = np.squeeze(gray_image)
    gray_image = gray_image.astype('uint8')

    faces = detect_faces(face_detection, gray_image)

    result = Result(frame=instance)
    result.save()

    for face_coordinates in faces:
        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]

        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion_text = emotion_labels[emotion_label_arg]

        color = (0, 0, 255)

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -50, 1, 2)

        Object(x1=x1, x2=x2, y1=y1, y2=y2, label=emotion_text, result=result).save()
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

    img_temp = NamedTemporaryFile(delete=True)
    _, buf = cv2.imencode(".jpg", bgr_image)
    img_temp.write(buf)

    result.image.save(f"{instance.id}.jpg", File(img_temp))
    result.save()
