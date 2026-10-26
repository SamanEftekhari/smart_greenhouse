from django.urls import path

from .views import (
    sensor_data,
    latest_sensors,
    sensor_history,
    sensors_page,
)

app_name = "monitoring"

urlpatterns = [

    path(
        "",
        sensors_page,
        name="sensors"
    ),

    path(
        "sensor-data/",
        sensor_data,
        name="sensor-data"
    ),

    path(
        "latest/",
        latest_sensors,
        name="latest-sensors"
    ),

    path(
        "history/<str:sensor_code>/",
        sensor_history,
        name="sensor-history"
    ),
]