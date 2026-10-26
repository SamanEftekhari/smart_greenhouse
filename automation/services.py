import json

import paho.mqtt.publish as mqtt_publish

from django.conf import settings
from django.db import transaction

from automation.models import AutomationRule


def send_actuator_command(actuator, status):
    """
    ارسال فرمان تجهیز از طریق MQTT
    """

    topic = f"greenhouse/actuators/{actuator.code}"

    payload = json.dumps({
        "actuator": actuator.code,
        "status": status,
    })

    try:
        mqtt_publish.single(
            topic,
            payload=payload,
            hostname=settings.MQTT_BROKER,
            port=settings.MQTT_PORT,
        )

        print(
            f"MQTT COMMAND -> {topic}: {payload}"
        )

        return True

    except Exception as e:

        print(
            f"MQTT ERROR -> {e}"
        )

        return False


def check_rule(rule):

    sensor = rule.sensor
    actuator = rule.actuator

    reading = sensor.readings.order_by(
        "-timestamp"
    ).first()

    if not reading:
        return False

    value = reading.value

    condition_met = False

    if rule.condition == "gt":
        condition_met = value > rule.threshold

    elif rule.condition == "lt":
        condition_met = value < rule.threshold

    elif rule.condition == "eq":
        condition_met = value == rule.threshold

    if not condition_met:
        return False

    if actuator.status == rule.target_status:
        return False

    with transaction.atomic():

        actuator.status = rule.target_status

        actuator.save(
            update_fields=["status"]
        )

    send_actuator_command(
        actuator,
        rule.target_status
    )

    return True


def run_automation():

    rules = AutomationRule.objects.filter(
        is_active=True
    ).select_related(
        "sensor",
        "actuator",
    )

    changed = []

    for rule in rules:

        if check_rule(rule):

            changed.append({
                "rule": rule.id,
                "sensor": rule.sensor.code,
                "actuator": rule.actuator.code,
                "status": rule.target_status,
            })

    return changed