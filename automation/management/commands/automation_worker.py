import time

from django.core.management.base import BaseCommand

from automation.services import run_automation


class Command(BaseCommand):

    help = "Run greenhouse automation continuously"

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.SUCCESS(
                "Automation worker started..."
            )
        )

        while True:

            try:

                changed = run_automation()

                if changed:

                    for item in changed:

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Automation: "
                                f"{item['sensor']} -> "
                                f"{item['actuator']} = "
                                f"{item['status']}"
                            )
                        )

                time.sleep(5)

            except KeyboardInterrupt:

                self.stdout.write(
                    self.style.WARNING(
                        "Automation worker stopped."
                    )
                )

                break

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Automation error: {e}"
                    )
                )

                time.sleep(5)