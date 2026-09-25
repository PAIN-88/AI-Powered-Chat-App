import os
import threading
import time
from django.apps import AppConfig


def run_scheduler_loop():
    from django.core.management import call_command
    print("Time capsule scheduler started... checking every 60 seconds.")
    while True:
        try:
            call_command("unlock_time_capsules")
        except Exception as e:
            print("Scheduler error:", e)
        time.sleep(60)


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            thread = threading.Thread(target=run_scheduler_loop, daemon=True)
            thread.start()