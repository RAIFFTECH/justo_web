from datetime import date, datetime

def fecha_corta(fecha):
    # Recibe un objeto date y devuelve una cadena tipo Abr-17-2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    return f"{meses[fecha.month - 1]}-{fecha.day:02d}-{fecha.year}"


def fecha_larga(fecha):
    # Recibe un objeto date y devuelve una cadena tipo Abril 17 de 2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return f"{meses[fecha.month - 1]} {fecha.day} de {fecha.year}"

hoy = date.today()


def fecha_año_mes_dia(fecha):
    # Recibe un objeto date y devuelve una cadena tipo 2025-04-17.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    return fecha.strftime("%Y-%m-%d")


def fecha_dia_mes_año(fecha):
    # Recibe un objeto date y devuelve una cadena tipo 17-04-2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    return fecha.strftime("%d-%m-%Y")

