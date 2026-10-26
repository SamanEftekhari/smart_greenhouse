from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Sensor, SensorReading


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "sensor_type",
        "zone",
        "status",
        "unit",
        "last_seen",
        "is_active",
    )

    list_filter = (
        "sensor_type",
        "status",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "zone__name",
    )


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "sensor",
        "value",
        "timestamp",
    )

    list_filter = ("sensor",)
    date_hierarchy = "timestamp"