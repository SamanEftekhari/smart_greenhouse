from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Greenhouse, Zone, Crop, Cultivation


@admin.register(Greenhouse)
class GreenhouseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "location",
        "area",
        "is_active",
    )

    search_fields = ("name", "code", "location")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "greenhouse",
        "area",
        "is_active",
    )

    list_filter = ("greenhouse", "is_active")
    search_fields = ("name", "code")


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name", "variety")
    search_fields = ("name", "variety")


@admin.register(Cultivation)
class CultivationAdmin(admin.ModelAdmin):
    list_display = (
        "crop",
        "zone",
        "start_date",
        "end_date",
        "quantity",
        "is_active",
    )

    list_filter = ("is_active", "crop")