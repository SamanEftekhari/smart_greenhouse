from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        include("greenhouse.urls")
    ),

    path(
        "api/monitoring/",
        include("monitoring.urls")
    ),

    path(
        "automation/",
        include("automation.urls")
    ),
]