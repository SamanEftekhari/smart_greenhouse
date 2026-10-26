
from django.db import models


class Sensor(models.Model):
    class SensorType(models.TextChoices):
        TEMPERATURE = "temperature", "دما"
        HUMIDITY = "humidity", "رطوبت هوا"
        SOIL_MOISTURE = "soil_moisture", "رطوبت خاک"
        CO2 = "co2", "دی‌اکسید کربن"
        LIGHT = "light", "شدت نور"
        PH = "ph", "اسیدیته"
        EC = "ec", "هدایت الکتریکی"

    class Status(models.TextChoices):
        ONLINE = "online", "آنلاین"
        OFFLINE = "offline", "آفلاین"
        ERROR = "error", "خطا"

    class DataSource(models.TextChoices):
        SIMULATION = "simulation", "داده آزمایشی"
        REAL = "real", "سنسور واقعی"

    zone = models.ForeignKey(
        "greenhouse.Zone",
        on_delete=models.CASCADE,
        related_name="sensors",
        verbose_name="زون",
    )
    name = models.CharField(max_length=150, verbose_name="نام سنسور")
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد سنسور",
    )
    sensor_type = models.CharField(
        max_length=30,
        choices=SensorType.choices,
        verbose_name="نوع سنسور",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OFFLINE,
        verbose_name="وضعیت سنسور",
    )
    data_source = models.CharField(
        max_length=10,
        choices=DataSource.choices,
        default=DataSource.SIMULATION,
        verbose_name="منبع داده",
    )
    unit = models.CharField(max_length=20, verbose_name="واحد اندازه‌گیری")
    min_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداقل مقدار مجاز",
    )
    max_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداکثر مقدار مجاز",
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین ارتباط",
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
        verbose_name = "سنسور"
        verbose_name_plural = "سنسورها"
        ordering = ["zone", "sensor_type", "name"]
        indexes = [
            models.Index(fields=["zone", "sensor_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class SensorReading(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name="سنسور",
    )
    value = models.FloatField(verbose_name="مقدار اندازه‌گیری‌شده")
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="زمان ثبت",
    )

    class Meta:
        verbose_name = "خوانش سنسور"
        verbose_name_plural = "خوانش‌های سنسورها"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sensor", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.sensor.code}: {self.value} ({self.timestamp})"
