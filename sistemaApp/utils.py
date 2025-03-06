from datetime import datetime

# Funciones auxiliares
def obtener_nombre_mes(numero_mes):
    numero_mes = int(numero_mes)
    MESES = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
    return MESES.get(numero_mes, "Mes desconocido")

def obtener_mes():
    return obtener_nombre_mes(datetime.now().month)

def generar_rango_meses(mes_a_predecir, periodos):
    mes_a_predecir = int(mes_a_predecir)
    anio_actual = datetime.now().year
    rango_meses = []
    for i in range(periodos):
        mes = mes_a_predecir - i - 1
        anio = anio_actual
        if mes <= 0:
            mes += 12
            anio -= 1
        rango_meses.append((mes, anio))
    return rango_meses