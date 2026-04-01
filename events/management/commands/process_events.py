# qubitgyanpro\events\management\commands\process_events.py

from django.core.management.base import BaseCommand
from events.retry import retry_failed_events


class Command(BaseCommand):
    help = "Retry failed events"

    def handle(self, *args, **kwargs):
        retry_failed_events()
        self.stdout.write(self.style.SUCCESS("Event retry completed"))

        