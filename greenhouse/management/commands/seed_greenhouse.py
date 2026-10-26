
from datetime import timedelta
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from greenhouse.models import Greenhouse, Zone, Crop, Cultivation
from monitoring.models import Sensor, SensorReading
from automation.models import Actuator, AutomationRule


class Command(BaseCommand):
    help = "Create sample data for the smart greenhouse project"

    ZONES = [
        ("ARIAN-SINA-01", "گلخانه ۱ آرین سینا", 1000),
        ("ARIAN-SHIMI-01", "گلخانه ۱ آرین شیمی", 900),
        ("ARIAN-RAKH-01", "گلخانه ۱ آرین رخ", 850),
        ("ARIAN-SINA-02", "گلخانه ۱ آرین سینا ۲", 950),
        ("ARIAN-SHIMI-02", "گلخانه ۱ آرین شیمی ۲", 800),
    ]

    SENSOR_CONFIG = [
        ("temperature", "دما", "°C", 10, 40, 24, 3),
        ("humidity", "رطوبت هوا", "%", 30, 90, 65, 8),
        ("soil_moisture", "رطوبت خاک", "%", 20, 80, 45, 10),
        ("co2", "دی‌اکسید کربن", "ppm", 300, 1500, 750, 120),
        ("light", "شدت نور", "lux", 1000, 50000, 18000, 6000),
        ("ph", "اسیدیته خاک", "pH", 4, 9, 6.5, 0.4),
        ("ec", "هدایت الکتریکی", "mS/cm", 0.5, 4, 2, 0.4),
    ]

    ACTUATOR_CONFIG = [
        ("fan", "فن تهویه"),
        ("pump", "پمپ آبیاری"),
        ("heater", "هیتر"),
        ("valve", "شیر برقی"),
        ("cooling", "سیستم خنک‌کننده"),
    ]

    CROPS = [
        ("گوجه‌فرنگی", "بریویو"),
        ("خیار", "گلخانه‌ای"),
        ("فلفل دلمه‌ای", "رنگی"),
        ("توت‌فرنگی", "گلخانه‌ای"),
        ("کاهو", "هیدروپونیک"),
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(1405)

        greenhouse, _ = Greenhouse.objects.get_or_create(
            code="GH-001",
            defaults={
                "name": "گلخانه ۱",
                "location": "مجموعه گلخانه‌های آرین",
                "area": 4500,
                "description": "گلخانه هوشمند چندبخشی؛ داده‌های سنسورها در این نسخه آزمایشی هستند.",
                "is_active": True,
            },
        )

        zones = []

        for index, (code, name, area) in enumerate(self.ZONES, start=1):
            zone, _ = Zone.objects.get_or_create(
                greenhouse=greenhouse,
                code=code,
                defaults={
                    "name": name,
                    "area": area,
                    "is_active": True,
                },
            )
            zones.append((index, zone))

        crops = []
        for name, variety in self.CROPS:
            crop, _ = Crop.objects.get_or_create(
                name=name,
                variety=variety,
                defaults={
                    "description": "محصول نمونه برای آزمایش سامانه گلخانه هوشمند",
                },
            )
            crops.append(crop)

        sensors_created = 0
        readings_created = 0
        actuators_created = 0
        rules_created = 0
        cultivations_created = 0

        now = timezone.now()
        start_date = timezone.localdate() - timedelta(days=35)

        for zone_index, zone in zones:
            # کشت نمونه برای هر زون
            crop = crops[(zone_index - 1) % len(crops)]

            _, created = Cultivation.objects.get_or_create(
                zone=zone,
                crop=crop,
                is_active=True,
                defaults={
                    "start_date": start_date,
                    "quantity": random.randint(500, 2500),
                    "end_date": None,
                },
            )
            cultivations_created += int(created)

            zone_sensors = {}

            # ساخت ۷ سنسور در هر زون
            for sensor_type, title, unit, min_value, max_value, center, spread in self.SENSOR_CONFIG:
                code_prefix = {
                    "temperature": "TEMP",
                    "humidity": "HUM",
                    "soil_moisture": "SOIL",
                    "co2": "CO2",
                    "light": "LIGHT",
                    "ph": "PH",
                    "ec": "EC",
                }[sensor_type]

                code = f"{code_prefix}-Z{zone_index}-01"

                sensor, created = Sensor.objects.get_or_create(
                    code=code,
                    defaults={
                        "zone": zone,
                        "name": f"{title} - {zone.name}",
                        "sensor_type": sensor_type,
                        "unit": unit,
                        "status": "online",
                        "min_value": min_value,
                        "max_value": max_value,
                        "last_seen": now,
                        "is_active": True,
                    },
                )

                sensors_created += int(created)
                zone_sensors[sensor_type] = sensor

                # وضعیت سنسور موجود را بی‌دلیل بازنویسی نمی‌کنیم.
                # اگر هیچ داده‌ای ندارد، ۴۸ نقطه در ۲۴ ساعت می‌سازیم.
                if not sensor.readings.exists():
                    readings = []

                    for step in range(48, 0, -1):
                        timestamp = now - timedelta(minutes=30 * step)

                        # تغییر ملایم در طول زمان، همراه با نویز نمونه
                        daily_wave = (
                            1.0
                            if timestamp.hour < 12
                            else -1.0
                        )

                        value = center + random.gauss(0, spread)
                        if sensor_type in ("temperature", "light"):
                            value += daily_wave * spread * 0.25

                        value = max(min_value, min(max_value, value))

                        reading = SensorReading(
                            sensor=sensor,
                            value=round(value, 2),
                        )

                        # bulk_create از auto_now_add در save معمولی عبور می‌کند؛
                        # بنابراین می‌توان زمان تاریخی را تنظیم کرد.
                        reading.timestamp = timestamp
                        readings.append(reading)

                    SensorReading.objects.bulk_create(readings, batch_size=500)
                    readings_created += len(readings)

            # ساخت تجهیزات کنترلی
            zone_actuators = {}

            for actuator_type, title in self.ACTUATOR_CONFIG:
                code = f"{actuator_type.upper()}-Z{zone_index}-01"

                actuator, created = Actuator.objects.get_or_create(
                    code=code,
                    defaults={
                        "zone": zone,
                        "name": f"{title} - {zone.name}",
                        "actuator_type": actuator_type,
                        "status": "off",
                        "is_active": True,
                    },
                )

                actuators_created += int(created)
                zone_actuators[actuator_type] = actuator

            # قوانین نمونه: دمای بالا => فن روشن؛ رطوبت پایین خاک => پمپ روشن
            rules = [
                (
                    zone_sensors["temperature"],
                    zone_actuators["fan"],
                    "gt",
                    30.0,
                    "on",
                ),
                (
                    zone_sensors["soil_moisture"],
                    zone_actuators["pump"],
                    "lt",
                    35.0,
                    "on",
                ),
            ]

            for sensor, actuator, condition, threshold, target_status in rules:
                _, created = AutomationRule.objects.get_or_create(
                    sensor=sensor,
                    actuator=actuator,
                    condition=condition,
                    threshold=threshold,
                    target_status=target_status,
                    defaults={"is_active": True},
                )
                rules_created += int(created)

        self.stdout.write(self.style.SUCCESS("ساخت داده‌های نمونه تمام شد."))
        self.stdout.write(f"گلخانه: {greenhouse.name}")
        self.stdout.write(f"زون‌ها: {len(zones)}")
        self.stdout.write(f"سنسورهای جدید: {sensors_created}")
        self.stdout.write(f"خوانش‌های تاریخی جدید: {readings_created}")
        self.stdout.write(f"تجهیزات جدید: {actuators_created}")
        self.stdout.write(f"قوانین جدید: {rules_created}")
        self.stdout.write(f"کشت‌های جدید: {cultivations_created}")
        self.stdout.write(
            self.style.WARNING(
                "توجه: مقادیر سنسورها آزمایشی‌اند و نباید به‌عنوان "
                "اندازه‌گیری واقعی تجهیزات استفاده شوند."
            )
        )
