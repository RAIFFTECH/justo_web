from django.apps import AppConfig

class UsuariosAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios_app'

    def ready(self):
        import usuarios_app.signals

