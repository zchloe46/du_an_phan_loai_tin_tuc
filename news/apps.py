from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Đoạn này đảm bảo scheduler chỉ chạy 1 lần khi server start
        import os
        if os.environ.get('RUN_MAIN', None) == 'true':
            from .scheduler import start_scheduler
            try:
                start_scheduler()
            except Exception as e:
                print(e)