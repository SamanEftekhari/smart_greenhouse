
from django.db import models


class Actuator(models.Model):
    class ActuatorType(models.TextChoices):
        FAN = "fan", "فن"
        PUMP = "pump", "پمپ"
        HEATER = "heater", "هیتر"
        VALVE = "valve", "شیر برقی"
        LIGHT = "light", "روشنایی"
        WINDOW = "window", "دریچه"
        COOLING = "cooling", "سیستم خنک‌کننده"

    class Status(models.TextChoices):
        ON = "on", "روشن"
        OFF = "off", "خاموش"
        OFFLINE = "offline", "آفلاین"
        ERROR = "error", "خطا"

    class ExecutionMode(models.TextChoices):
        SIMULATION = "simulation", "اجرای شبیه‌سازی"
        REAL = "real", "اجرای واقعی"

    zone = models.ForeignKey(
        "greenhouse.Zone",
        on_delete=models.CASCADE,
        related_name="actuators",
        verbose_name="زون",
    )
    name = models.CharField(max_length=150, verbose_name="نام تجهیز")
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تجهیز",
    )
    actuator_type = models.CharField(
        max_length=30,
        choices=ActuatorType.choices,
        verbose_name="نوع تجهیز",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OFF,
        verbose_name="وضعیت تجهیز",
    )
    execution_mode = models.CharField(
        max_length=10,
        choices=ExecutionMode.choices,
        default=ExecutionMode.SIMULATION,
        verbose_name="روش اجرای فرمان",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    class Meta:
        verbose_name = "تجهیز کنترلی"
        verbose_name_plural = "تجهیزات کنترلی"
        ordering = ["zone", "actuator_type", "name"]
        indexes = [
            models.Index(fields=["zone", "actuator_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AutomationRule(models.Model):
    class Condition(models.TextChoices):
        GT = "gt", "بزرگ‌تر از"
        LT = "lt", "کوچک‌تر از"
        EQ = "eq", "برابر با"

    class TargetStatus(models.TextChoices):
        ON = "on", "روشن"
        OFF = "off", "خاموش"

    sensor = models.ForeignKey(
        "monitoring.Sensor",
        on_delete=models.CASCADE,
        related_name="automation_rules",
        verbose_name="سنسور محرک",
    )
    actuator = models.ForeignKey(
        Actuator,
        on_delete=models.CASCADE,
        related_name="automation_rules",
        verbose_name="تجهیز هدف",
    )
    condition = models.CharField(
        max_length=5,
        choices=Condition.choices,
        verbose_name="شرط",
    )
    threshold = models.FloatField(verbose_name="مقدار آستانه")
    target_status = models.CharField(
        max_length=5,
        choices=TargetStatus.choices,
        verbose_name="وضعیت هدف",
    )
    is_active = models.BooleanField(default=True, verbose_name="قانون فعال")

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    class Meta:
        verbose_name = "قانون اتوماسیون"
        verbose_name_plural = "قوانین اتوماسیون"
        ordering = ["sensor", "actuator"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sensor",
                    "actuator",
                    "condition",
                    "threshold",
                    "target_status",
                ],
                name="unique_automation_rule",
            )
        ]

    def __str__(self):
        return (
            f"{self.sensor.code} {self.get_condition_display()} "
            f"{self.threshold} → {self.actuator.name}: "
            f"{self.get_target_status_display()}"
        )
