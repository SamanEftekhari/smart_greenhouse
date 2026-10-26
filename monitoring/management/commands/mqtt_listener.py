
from django.core.management.base import BaseCommand, CommandError

from monitoring.mqtt_client import start_mqtt


class Command(BaseCommand):
    help = "Start the greenhouse MQTT sensor listener"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Starting greenhouse MQTT listener...")
        )

        try:
            start_mqtt()
        except KeyboardInterrupt:
            self.stdout.write("MQTT listener stopped.")
        except Exception as exc:
            raise CommandError(f"MQTT listener failed: {exc}") from exc
