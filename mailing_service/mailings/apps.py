from django.apps import AppConfig


class MailingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'

    def ready(self):
        # Временно закомментируем запуск планировщика
        # try:
        #     from .scheduler import start_scheduler
        #     start_scheduler()
        # except Exception as e:
        #     print(f"Ошибка при запуске планировщика: {e}")
        pass
