from django.conf.urls import url
from django.urls import include
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from wrappr_backend.detection.models import Context, Frame, Result, Object


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = ("id", "url")


class FrameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Frame
        fields = ("id", "image", "url", "context")


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ("id", "image", "frame",)


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Object
        fields = ("result", "x1", "x2", "y1", "y2", "label")


class ContextViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Context.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    serializer_class = ContextSerializer


class FrameViewSet(viewsets.ModelViewSet):
    serializer_class = FrameSerializer

    def get_queryset(self): return Frame.objects.filter(context__user=self.request.user)


# TODO: Maybe remove read-only depending on development
class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResultSerializer

    def get_queryset(self): return Result.objects.filter(frame__context__user=self.request.user)


class ObjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ObjectSerializer
    queryset = Object.objects.all()


router = DefaultRouter()
router.register(r"contexts", ContextViewSet, base_name="context")
router.register(r"frames", FrameViewSet, base_name="frame")
router.register(r"results", ResultViewSet, base_name="result")
router.register(r"objects", ObjectViewSet, base_name="object")

urlpatterns = [
    url(r"^", include(router.urls)),
]
