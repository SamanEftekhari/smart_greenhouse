from django.urls import path

from .views import (
    dashboard,
    greenhouse_list,
    zone_list,
)

app_name = "greenhouse"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("greenhouses/", greenhouse_list, name="greenhouses"),
    path("zones/", zone_list, name="zones"),
]