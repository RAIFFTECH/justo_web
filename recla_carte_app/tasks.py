from celery import shared_task
import time
import redis
from datetime import datetime
from oficinas_app.models  import OFICINAS
from justo_creditos import perdida_esperada  # Ajusta si es otro archivo

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@shared_task(bind=True)
def ejecutar_modelo_task(self, oficina_id, fecha_str):
    try:
        oficina = OFICINAS.objects.get(id=oficina_id)
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        print(f"Ejecutando tarea para la fecha: {fecha_str}")

        pe_mes = perdida_esperada(oficina, fecha)

        # Simulamos 5 pasos con avance
        for paso in range(5):
            # Aquí llamarías a tu lógica paso a paso
            print(f"[{datetime.now()}] Ejecutando paso {paso + 1}")
            
            # Simula trabajo
            time.sleep(2)  # Reemplaza con trabajo real

            porcentaje = int((paso + 1) / 5 * 100)
            r.set(f"progreso:{self.request.id}", porcentaje)

        # Al final marcamos como 100%
        r.set(f"progreso:{self.request.id}", 100)

    except Exception as e:
        r.set(f"progreso:{self.request.id}", -1)
        raise e

from celery import shared_task
import time

@shared_task
def tarea_lenta():
    for i in range(1, 20):
        print(f"Progreso: {i*20}%")
        time.sleep(2)
    print("¡Tarea completada!")
    return "Tarea completada"