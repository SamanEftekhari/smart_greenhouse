from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Actuator


def actuators_page(request):
    actuators = Actuator.objects.filter(
        is_active=True
    ).select_related("zone", "zone__greenhouse")

    return render(
        request,
        "automation/actuators.html",
        {
            "actuators": actuators,
        }
    )


@csrf_exempt
def actuator_control(request, actuator_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405
        )

    actuator = get_object_or_404(
        Actuator,
        id=actuator_id,
        is_active=True
    )

    try:
        import json

        data = json.loads(request.body)
        command = data.get("status")

        if command not in ["on", "off"]:
            return JsonResponse(
                {
                    "error": "status must be on or off"
                },
                status=400
            )

        actuator.status = command
        actuator.save(
            update_fields=["status"]
        )

        return JsonResponse({
            "success": True,
            "id": actuator.id,
            "code": actuator.code,
            "status": actuator.status,
            "timestamp": timezone.now(),
        })

    except Exception as e:

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

from django.http import JsonResponse

from .services import run_automation


def run_automation_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required"
            },
            status=405
        )

    try:

        changed = run_automation()

        return JsonResponse({
            "success": True,
            "changed": changed,
        })

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "error": str(e),
            },
            status=500
        )