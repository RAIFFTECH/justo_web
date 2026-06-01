from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog
from .middleware import get_current_user
from .audit_config import AUDIT_MODELS
from hecho_economico_app.models import HECHO_ECONO
from django.conf import settings


@receiver(post_save)
def audit_log_create_or_update(sender, instance, created, **kwargs):
    if not getattr(settings, 'AUDIT_LOG_ENABLED', True):  # Verificar si está habilitado
        return
    if sender in [HECHO_ECONO]:  # Agrega otros modelos a auditar
        user = get_current_user()  # O request.user si estás en una vista

        if created:
            AuditLog.objects.create(
                action='C',
                user=user,
                model_name=sender._meta.model_name,
                object_id=instance.pk,
                changes=None,
            )
        else:  # Para modificaciones
            original = sender.objects.get(pk=instance.pk)
            if has_changes(original, instance):
                AuditLog.objects.create(
                    action='M',
                    user=user,
                    model_name=sender._meta.model_name,
                    object_id=instance.pk,
                    changes=get_changes(original, instance),
                )

@receiver(post_delete)
def audit_log_delete(sender, instance, **kwargs):
    if not getattr(settings, 'AUDIT_LOG_ENABLED', True):  # Verificar si está habilitado
        return
    if sender in [HECHO_ECONO]:  # Agrega aquí otros modelos a auditar
        user = get_current_user()  # O request.user si estás en una vista

        AuditLog.objects.create(
            action='D',
            user=user,
            model_name=sender._meta.model_name,
            object_id=instance.pk,
            changes=None,  # Aquí puedes agregar información del objeto eliminado si lo deseas
        )

def has_changes(original, instance):
    if not getattr(settings, 'AUDIT_LOG_ENABLED', True):  # Verificar si está habilitado
        return
    fields_to_audit = ['fecha','anulado', 'protegido','canal','banco','cheque','beneficiario']
    for field in fields_to_audit:
        if getattr(original, field) != getattr(instance, field):
            return True
    return False

def get_changes(original, instance):
    if not getattr(settings, 'AUDIT_LOG_ENABLED', True):  # Verificar si está habilitado
        return
    changes = {}
    fields_to_audit = ['fecha','anulado', 'protegido','canal','banco','cheque','beneficiario']
    for field in fields_to_audit:
        if getattr(original, field) != getattr(instance, field):
            changes[field] = {
                'old': getattr(original, field),
                'new': getattr(instance, field),
            }
    return changes
