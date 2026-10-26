from django.shortcuts import render
from django.db.models import Count

from .models import Greenhouse, Zone
from monitoring.models import Sensor
from automation.models import Actuator
from django.db import models
from django.db.models import Count, OuterRef, Subquery


from django.shortcuts import render
from django.db.models import Count, OuterRef, Subquery

from .models import Greenhouse, Zone
from monitoring.models import Sensor, SensorReading
from automation.models import Actuator



from django.shortcuts import render
from django.db.models import Count, Q, OuterRef, Subquery

from .models import Greenhouse, Zone
from monitoring.models import Sensor, SensorReading
from automation.models import Actuator


def dashboard(request):
    greenhouses = Greenhouse.objects.filter(is_active=True)
    sensors = Sensor.objects.filter(is_active=True)
    actuators = Actuator.objects.filter(is_active=True)

    latest_reading = SensorReading.objects.filter(
        sensor=OuterRef("pk")
    ).order_by("-timestamp")

    zones = (
        Zone.objects.filter(is_active=True)
        .select_related("greenhouse")
        .annotate(
            sensor_count=Count(
                "sensors",
                filter=Q(sensors__is_active=True),
                distinct=True,
            ),
            online_count=Count(
                "sensors",
                filter=Q(
                    sensors__is_active=True,
                    sensors__status="online",
                ),
                distinct=True,
            ),
            offline_count=Count(
                "sensors",
                filter=Q(
                    sensors__is_active=True,
                    sensors__status="offline",
                ),
                distinct=True,
            ),
            error_count=Count(
                "sensors",
                filter=Q(
                    sensors__is_active=True,
                    sensors__status="error",
                ),
                distinct=True,
            ),
        )
        .order_by("greenhouse__name", "name")
    )

    sensor_latest_values = sensors.select_related(
        "zone",
        "zone__greenhouse",
    ).annotate(
        latest_value=Subquery(latest_reading.values("value")[:1]),
        latest_timestamp=Subquery(
            latest_reading.values("timestamp")[:1]
        ),
    )

    context = {
        "greenhouse_count": greenhouses.count(),
        "zone_count": zones.count(),
        "sensor_count": sensors.count(),
        "online_sensors": sensors.filter(status="online").count(),
        "offline_sensors": sensors.filter(status="offline").count(),
        "error_sensors": sensors.filter(status="error").count(),
        "actuator_count": actuators.count(),
        "actuators_on": actuators.filter(status="on").count(),
        "actuators_off": actuators.filter(status="off").count(),
        "zones": zones,
        "recent_sensors": sensor_latest_values.order_by(
            "-latest_timestamp"
        )[:10],
    }

    return render(
        request,
        "greenhouse/dashboard.html",
        context,
    )

def greenhouse_list(request):
    greenhouses = Greenhouse.objects.all().prefetch_related("zones")

    return render(
        request,
        "greenhouse/greenhouses.html",
        {
            "greenhouses": greenhouses,
        },
    )


def zone_list(request):
    zones = Zone.objects.all().select_related("greenhouse")

    return render(
        request,
        "greenhouse/zones.html",
        {
            "zones": zones,
        },
    )