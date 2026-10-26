from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Actuator, AutomationRule


@admin.register(Actuator)
class ActuatorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "actuator_type",
        "zone",
        "status",
        "is_active",
    )

    list_filter = (
        "actuator_type",
        "status",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = (
        "sensor",
        "actuator",
        "condition",
        "threshold",
        "target_status",
        "is_active",
    )

    list_filter = (
        "condition",
        "target_status",
        "is_active",
    )