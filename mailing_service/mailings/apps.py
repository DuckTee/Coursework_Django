from django.apps import AppConfig

from apscheduler.schedulers.background import BackgroundScheduler
from .views import send_mailing


class MailingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'

    def ready(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_mailing, 'interval', seconds=300)
        scheduler.start()
