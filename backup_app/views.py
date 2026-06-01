import shutil, os
from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
# from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Backup
import subprocess
from justo_proy import settings

# ESTO ES PARA MARIADB
# def backup_database(request):
#     # Nombre del archivo de copia de seguridad
#     backup_filename = f"backup_{timezone.now().strftime('%Y-%m-%d_%H-%M-%S')}.sql"

#     # Ruta completa al archivo de copia de seguridad
#     backup_path = f"{settings.BASE_DIR}/{backup_filename}"

#     # Comando mysqldump
#     db_user = settings.DATABASES['default']['USER']
#     db_password = settings.DATABASES['default']['PASSWORD']
#     db_name = settings.DATABASES['default']['NAME']
#     command = f"mysqldump --routines --triggers --events -u {db_user} -p{db_password} {db_name} > {backup_path}"
#     # command = f"mysqldump -u {db_user} -p{db_password} {db_name} > {backup_path}"

#     # Ejecutar el comando mysqldump
#     subprocess.run(command, shell=True)

#     # Registrar la copia de seguridad en la base de datos
#     backup = Backup(filename=(backup_filename), usuario=request.user)
#     backup.save()
    
#     messages.success(request, f"Copia de seguridad creada correctamente: {backup_filename}")

#     return redirect('inicio')  # a donde quieras volver

#     # return HttpResponse(f"Copia de seguridad creada correctamente: {backup_filename}")

# def restore_backup(request):
#     if request.method == 'POST':
#         # Nombre del archivo de copia de seguridad enviado desde el formulario
#         backup_filename = request.POST.get('backup_filename', None)

#         if backup_filename:
#             # Ruta completa al archivo de copia de seguridad
#             backup_path = f"{settings.BASE_DIR}/{backup_filename}"
                        
#             # Comando mysql para restaurar la base de datos
#             db_user = settings.DATABASES['default']['USER']
#             db_password = settings.DATABASES['default']['PASSWORD']
#             db_name = settings.DATABASES['default']['NAME']
#             command = f"mysql -u {db_user} -p{db_password} {db_name} < {backup_path}"

#             # Ejecutar el comando mysql
#             subprocess.run(command, shell=True)

#             messages.success(request, f"La restauración de la copia de seguridad se ha completado correctamente.")

#             return redirect('inicio')  # a donde quieras volver

#             # return HttpResponse("La restauración de la copia de seguridad se ha completado correctamente.")
#         else:
#             # return HttpResponse("No se ha proporcionado un nombre de archivo de copia de seguridad.")
#             messages.error(request, "No se ha proporcionado un nombre de archivo de copia de seguridad.")
#             return redirect('inicio')

#     else:
#         backups = Backup.objects.all()
#         return render(request, 'restore_backup.html', {'backups': backups})


def backup_database(request):
    
    # 📁 carpeta backups
    backup_dir = os.path.join(settings.BASE_DIR, 'copias_de_seguridad')
    os.makedirs(backup_dir, exist_ok=True)

    # 📄 nombre archivo
    backup_filename = f"backup_{timezone.now().strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3"

    # 📍 rutas
    db_path = settings.DATABASES['default']['NAME']
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        # 🔥 copiar archivo
        shutil.copy(db_path, backup_path)

        # 🔥 guardar registro
        backup = Backup(filename=backup_filename, usuario=request.user)
        backup.save()

        messages.success(request, f"✅ Backup creado correctamente: {backup_filename}")

    except Exception as e:
        messages.error(request, f"❌ Error al crear backup: {str(e)}")

    return redirect('inicio')


def restore_backup(request):
    
    if request.method == 'POST':

        backup_filename = request.POST.get('backup_filename')

        if not backup_filename:
            messages.error(request, "❌ No se seleccionó ningún archivo.")
            return redirect('inicio')

        backup_dir = os.path.join(settings.BASE_DIR, 'copias_de_seguridad')
        backup_path = os.path.join(backup_dir, backup_filename)

        db_path = settings.DATABASES['default']['NAME']

        try:
            # 🔴 MUY IMPORTANTE: cerrar conexiones
            connections.close_all()

            # 🔥 restaurar (reemplazar archivo)
            shutil.copy(backup_path, db_path)

            messages.success(request, "✅ Restauración completada correctamente.")

        except Exception as e:
            messages.error(request, f"❌ Error al restaurar: {str(e)}")

        return redirect('inicio')

    else:
        backups = Backup.objects.all().order_by('-id')

        return render(request, 'restore_backup.html', {
            'backups': backups
        })