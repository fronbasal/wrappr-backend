from wrappr_backend.detection.models import Result, Frame, Context, Object
from django.contrib import admin
from django.contrib.admin.decorators import register


@register(Context)
class ContextAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Result)
admin.site.register(Frame)
admin.site.register(Object)
