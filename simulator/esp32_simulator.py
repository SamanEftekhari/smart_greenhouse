import json
import random
import time

import paho.mqtt.client as mqtt


# =========================================================
# CONFIG
# =========================================================

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

DEVICE_ID = "ESP32-Z1-01"

# ---------------------------------------------------------
# Actuator
# ---------------------------------------------------------

FAN_COMMAND_TOPIC = (
    "greenhouse/actuators/FAN-Z1-01"
)

FAN_STATUS_TOPIC = (
    "greenhouse/status/FAN-Z1-01"
)

# ---------------------------------------------------------
# Device
# ---------------------------------------------------------

DEVICE_STATUS_TOPIC = (
    f"greenhouse/status/{DEVICE_ID}"
)

# ---------------------------------------------------------
# Sensors
# ---------------------------------------------------------

SENSOR_BASE_TOPIC = "greenhouse/sensors"


# =========================================================
# VIRTUAL SENSOR VALUES
# =========================================================

temperature = 26.0
humidity = 65.0
soil_moisture = 42.0
ec = 1.8
ph = 6.2

fan_status = "OFF"


# =========================================================
# MQTT CALLBACK
# =========================================================

def on_connect(client, userdata, flags, rc):

    print()
    print("=" * 60)

    if rc == 0:

        print("ESP32 SIMULATOR MQTT CONNECTED")

        client.subscribe(
            FAN_COMMAND_TOPIC
        )

        print(
            "Subscribed:",
            FAN_COMMAND_TOPIC
        )

        client.publish(
            DEVICE_STATUS_TOPIC,
            "ONLINE",
            retain=True
        )

        client.publish(
            FAN_STATUS_TOPIC,
            fan_status,
            retain=True
        )

    else:

        print(
            "MQTT connection failed:",
            rc
        )


def on_disconnect(
    client,
    userdata,
    rc,
):

    print(
        "MQTT disconnected:",
        rc
    )


def on_message(
    client,
    userdata,
    msg,
):

    global fan_status

    topic = msg.topic

    payload = msg.payload.decode(
        "utf-8"
    ).strip()

    print()
    print("MQTT COMMAND")
    print("Topic:", topic)
    print("Payload:", payload)

    if topic != FAN_COMMAND_TOPIC:
        return

    if payload.upper() == "ON":

        fan_status = "ON"

        print(
            "VIRTUAL RELAY => ON"
        )

        client.publish(
            FAN_STATUS_TOPIC,
            "ON",
            retain=True
        )

    elif payload.upper() == "OFF":

        fan_status = "OFF"

        print(
            "VIRTUAL RELAY => OFF"
        )

        client.publish(
            FAN_STATUS_TOPIC,
            "OFF",
            retain=True
        )

    else:

        print(
            "Unknown command:",
            payload
        )


# =========================================================
# SENSOR SIMULATION
# =========================================================

def simulate_sensors():

    global temperature
    global humidity
    global soil_moisture
    global ec
    global ph

    # -----------------------------------------------------
    # Temperature
    # -----------------------------------------------------

    if fan_status == "ON":

        temperature -= 0.08

    else:

        temperature += 0.05

    temperature += random.uniform(
        -0.08,
        0.08
    )

    temperature = max(
        15,
        min(40, temperature)
    )

    # -----------------------------------------------------
    # Humidity
    # -----------------------------------------------------

    humidity += random.uniform(
        -0.5,
        0.5
    )

    humidity = max(
        30,
        min(95, humidity)
    )

    # -----------------------------------------------------
    # Soil moisture
    # -----------------------------------------------------

    soil_moisture -= random.uniform(
        0.02,
        0.10
    )

    if soil_moisture < 30:

        soil_moisture += 0.8

    soil_moisture = max(
        20,
        min(80, soil_moisture)
    )

    # -----------------------------------------------------
    # EC
    # -----------------------------------------------------

    ec += random.uniform(
        -0.03,
        0.03
    )

    ec = max(
        0.5,
        min(3.5, ec)
    )

    # -----------------------------------------------------
    # pH
    # -----------------------------------------------------

    ph += random.uniform(
        -0.03,
        0.03
    )

    ph = max(
        4.5,
        min(8.0, ph)
    )


# =========================================================
# PUBLISH SENSOR
# =========================================================

def publish_sensor(
    client,
    sensor_code,
    value,
):

    topic = (
        f"{SENSOR_BASE_TOPIC}/"
        f"{sensor_code}"
    )

    payload = {
        "device": DEVICE_ID,
        "sensor": sensor_code,
        "value": round(
            value,
            2
        ),
    }

    client.publish(
        topic,
        json.dumps(payload)
    )

    print(
        f"SENSOR | "
        f"{sensor_code} = "
        f"{payload['value']}"
    )


# =========================================================
# PUBLISH ALL SENSORS
# =========================================================

def publish_all_sensors(
    client
):

    simulate_sensors()

    publish_sensor(
        client,
        "TEMP-Z1-01",
        temperature
    )

    publish_sensor(
        client,
        "HUM-Z1-01",
        humidity
    )

    publish_sensor(
        client,
        "SOIL-Z1-01",
        soil_moisture
    )

    publish_sensor(
        client,
        "EC-Z1-01",
        ec
    )

    publish_sensor(
        client,
        "PH-Z1-01",
        ph
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print(" SMART GREENHOUSE")
    print(" ESP32 VIRTUAL DEVICE")
    print("=" * 60)

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=DEVICE_ID,
    )

    client.on_connect = on_connect

    client.on_disconnect = on_disconnect

    client.on_message = on_message

    print(
        f"Connecting to MQTT "
        f"{MQTT_BROKER}:{MQTT_PORT}"
    )

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60,
    )

    client.loop_start()

    try:

        while True:

            if client.is_connected():

                publish_all_sensors(
                    client
                )

            else:

                print(
                    "Waiting for MQTT..."
                )

            time.sleep(5)

    except KeyboardInterrupt:

        print()
        print(
            "Stopping ESP32 simulator..."
        )

        client.publish(
            DEVICE_STATUS_TOPIC,
            "OFFLINE",
            retain=True
        )

        client.loop_stop()

        client.disconnect()


if __name__ == "__main__":

    main()