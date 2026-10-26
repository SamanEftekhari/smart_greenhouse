from datetime import timedelta
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Sensor, SensorReading


@csrf_exempt
def sensor_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        sensor_code = data.get("sensor")
        value = float(data.get("value"))

        if not sensor_code:
            return JsonResponse(
                {"error": "sensor is required"},
                status=400
            )

        sensor = Sensor.objects.get(code=sensor_code)

        reading = SensorReading.objects.create(
            sensor=sensor,
            value=value,
        )

        sensor.last_seen = timezone.now()
        sensor.status = "online"
        sensor.save(
            update_fields=["last_seen", "status"]
        )

        return JsonResponse({
            "success": True,
            "sensor": sensor.code,
            "value": reading.value,
            "timestamp": reading.timestamp,
        })

    except Sensor.DoesNotExist:
        return JsonResponse(
            {"error": "Sensor not found"},
            status=404
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=400
        )


def latest_sensors(request):

    sensors = Sensor.objects.filter(
        is_active=True
    ).select_related("zone")

    result = []

    for sensor in sensors:

        reading = sensor.readings.order_by(
            "-timestamp"
        ).first()

        result.append({
            "name": sensor.name,
            "code": sensor.code,
            "sensor_type": sensor.sensor_type,
            "unit": sensor.unit,
            "status": sensor.status,
            "zone": sensor.zone.name,
            "value": reading.value if reading else None,
            "timestamp": (
                reading.timestamp.isoformat()
                if reading else None
            ),
        })

    return JsonResponse({
        "sensors": result
    })


def sensor_history(request, sensor_code):

    try:
        sensor = Sensor.objects.get(
            code=sensor_code,
            is_active=True
        )

    except Sensor.DoesNotExist:
        return JsonResponse(
            {"error": "Sensor not found"},
            status=404
        )

    try:
        hours = int(
            request.GET.get("hours", 6)
        )
    except ValueError:
        hours = 6

    since = (
        timezone.now()
        - timedelta(hours=hours)
    )

    readings = SensorReading.objects.filter(
        sensor=sensor,
        timestamp__gte=since
    ).order_by("timestamp")

    data = []

    for reading in readings:

        data.append({
            "value": reading.value,
            "timestamp": reading.timestamp.isoformat(),
        })

    return JsonResponse({
        "sensor": sensor.code,
        "name": sensor.name,
        "unit": sensor.unit,
        "data": data,
    })


def sensors_page(request):

    sensors = Sensor.objects.filter(
        is_active=True
    ).select_related(
        "zone",
        "zone__greenhouse"
    )

    zones = sensors.values(
        "zone_id",
        "zone__name"
    ).distinct()

    sensor_types = Sensor.SENSOR_TYPES

    context = {
        "sensors": sensors,
        "zones": zones,
        "sensor_types": sensor_types,
    }

    return render(
        request,
        "monitoring/sensors.html",
        context
    )