
from django.db import models


class Greenhouse(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام گلخانه")
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد گلخانه",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="موقعیت مکانی",
    )
    area = models.FloatField(default=0, verbose_name="مساحت")
    description = models.TextField(blank=True, verbose_name="توضیحات")
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
        verbose_name = "گلخانه"
        verbose_name_plural = "گلخانه‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Zone(models.Model):
    class OperationMode(models.TextChoices):
        SIMULATION = "simulation", "شبیه‌سازی"
        REAL = "real", "واقعی"
        HYBRID = "hybrid", "ترکیبی"

    greenhouse = models.ForeignKey(
        Greenhouse,
        on_delete=models.CASCADE,
        related_name="zones",
        verbose_name="گلخانه",
    )
    name = models.CharField(max_length=150, verbose_name="نام زون")
    code = models.CharField(max_length=50, verbose_name="کد زون")
    area = models.FloatField(default=0, verbose_name="مساحت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    operation_mode = models.CharField(
        max_length=10,
        choices=OperationMode.choices,
        default=OperationMode.SIMULATION,
        verbose_name="حالت کار زون",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    class Meta:
        verbose_name = "زون"
        verbose_name_plural = "زون‌ها"
        ordering = ["greenhouse", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["greenhouse", "code"],
                name="unique_zone_code_per_greenhouse",
            )
        ]

    def __str__(self):
        return f"{self.greenhouse.name} - {self.name}"


class Crop(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام محصول")
    variety = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="رقم محصول",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "variety"],
                name="unique_crop_name_variety",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.variety}" if self.variety else self.name


class Cultivation(models.Model):
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name="cultivations",
        verbose_name="زون",
    )
    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name="cultivations",
        verbose_name="محصول",
    )
    start_date = models.DateField(verbose_name="تاریخ شروع کشت")
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان کشت",
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد یا مقدار کشت",
    )
    is_active = models.BooleanField(default=True, verbose_name="کشت فعال")

    class Meta:
        verbose_name = "دوره کشت"
        verbose_name_plural = "دوره‌های کشت"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.crop} - {self.zone}"
