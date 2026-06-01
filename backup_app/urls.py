from django.urls import path
from .views import backup_database, restore_backup

urlpatterns = [
    path('backup/', backup_database, name='backup_bd'),
    path('restore/', restore_backup, name='restore_backup'),

]
