
import json

import paho.mqtt.client as mqtt
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

from monitoring.models import Sensor, SensorReading

SENSOR_TOPIC = "greenhouse/sensors/#"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"MQTT connection failed: {reason_code}")
        return

    print(f"MQTT connected: {reason_code}")
    client.subscribe(SENSOR_TOPIC, qos=1)
    print(f"Subscribed to: {SENSOR_TOPIC}")



def save_sensor_data(data):
    sensor_code = data.get("sensor")
    if not sensor_code:
        raise ValueError("Sensor code is missing")

    if "value" not in data:
        raise ValueError("Sensor value is missing")

    sensor = Sensor.objects.get(code=sensor_code)

    SensorReading.objects.create(
        sensor=sensor,
        value=float(data["value"]),
    )

    sensor.status = "online"
    sensor.last_seen = timezone.now()
    sensor.save(update_fields=["status", "last_seen"])

    return sensor_code


def on_message(client, userdata, msg):
    close_old_connections()

    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        sensor_code = save_sensor_data(data)
        print(f"MQTT OK: {sensor_code} = {data.get('value', data.get('flow_rate'))}")

    except Sensor.DoesNotExist:
        print("MQTT ERROR: Sensor not found in Django database")

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"MQTT ERROR: Invalid sensor data: {exc}")

    except Exception as exc:
        print(f"MQTT ERROR: {type(exc).__name__}: {exc}")

    finally:
        close_old_connections()


def start_mqtt():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="django-greenhouse-listener",
    )

    client.on_connect = on_connect
    client.on_message = on_message

    broker = getattr(settings, "MQTT_BROKER", "127.0.0.1")
    port = getattr(settings, "MQTT_PORT", 1883)

    print(f"Connecting to MQTT broker {broker}:{port} ...")
    client.connect(broker, port, keepalive=60)

    print("MQTT listener is running. Press Ctrl+C to stop.")
    client.loop_forever()
