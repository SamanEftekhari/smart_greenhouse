from django.urls import path

from .views import (
    actuators_page,
    actuator_control,
    run_automation_api,
)

app_name = "automation"

urlpatterns = [

    path(
        "",
        actuators_page,
        name="actuators"
    ),

    path(
        "control/<int:actuator_id>/",
        actuator_control,
        name="actuator-control"
    ),

    path(
        "run/",
        run_automation_api,
        name="run-automation"
    ),
]