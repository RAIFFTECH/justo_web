from django.apps import AppConfig

class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditoria_app'

    def ready(self):
        import auditoria_app.signals  # Asegúrate de que este import esté aquí
