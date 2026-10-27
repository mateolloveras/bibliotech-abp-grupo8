import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src import datos, eda, modelo, negocio

FECHA_DE_LA_DEMO = pd.Timestamp("2026-10-27")


def titulo(texto):
    print("")
    print("=" * 70)
    print(texto)
    print("=" * 70)


def main():
    prestamos, usuarios, catalogo = datos.cargar_todo()
    entrenado, metricas = modelo.entrenar_modelo(prestamos)

    titulo("1. Carga y control de calidad de datos (RF1 y RF2)")
    print(datos.informe_de_calidad(prestamos, "prestamos_historicos.csv"))

    titulo("2. Análisis exploratorio (RF3, RF4 y RF5)")
    print(eda.imprimir_resumen(prestamos))
    print("")
    print(eda.tasa_de_mora_por_sede(prestamos))

    titulo("3. CF-03 / CF-04 - Autenticación")
    print(negocio.autenticar(usuarios, "gino.lencina@ispc.edu.ar", "Biblio2026*")["mensaje"])
    print(negocio.autenticar(usuarios, "gino.lencina@ispc.edu.ar", "ClaveErronea123")["mensaje"])

    titulo("4. CF-01 / CF-02 - Alta de usuarios")
    alta = negocio.registrar_usuario(usuarios, "Juan Pérez", "jperez@ispc.edu.ar", "Estudiante")
    print(f"{alta['mensaje']} (ID asignado: {alta['ID_Usuario']})")
    print(negocio.registrar_usuario(usuarios, "", "test@ispc.edu.ar", "Estudiante")["mensaje"])
    usuarios = alta["usuarios"]

    titulo("5. BT-03 - Búsqueda en el catálogo con límite de 100 caracteres")
    busqueda = negocio.buscar_en_catalogo(catalogo, "Python")
    print(f"Resultados para 'Python': {len(busqueda['resultados'])}")
    excedida = negocio.buscar_en_catalogo(catalogo, "a" * 101)
    print(excedida["avisos"][0])

    titulo("6. BT-01 - Validación de días de préstamo (valores límite)")
    for dias in [0, 1, 14, 15]:
        resultado = negocio.validar_dias_prestamo(dias)
        estado = "aceptado" if resultado["ok"] else f"rechazado -> {resultado['mensaje']}"
        print(f"  {dias} días: {estado}")

    titulo("7. BT-02 - Bloqueo por mora y BT-07 - Falta de stock")
    print(negocio.registrar_reserva(usuarios, catalogo, prestamos, "U-012", "L-001", 7)["mensaje"])
    print(negocio.registrar_reserva(usuarios, catalogo, prestamos, "U-005", "L-205", 7)["mensaje"])

    titulo("8. Reserva válida + predicción de riesgo (PI-02 y BT-06)")
    reserva = negocio.registrar_reserva(
        usuarios, catalogo, prestamos, "U-005", "L-007", 14, fecha_prestamo=FECHA_DE_LA_DEMO
    )
    print(reserva["mensaje"])
    prestamo = reserva["prestamo"]
    riesgo = modelo.predecir_riesgo(
        entrenado,
        prestamo["Categoria_Libro"],
        prestamo["Tipo_Usuario"],
        prestamo["Demoras_Previas"],
        prestamo["Sede"],
    )
    print(riesgo["mensaje"])
    print("")
    caso_bt06 = modelo.predecir_riesgo(entrenado, "Informática", "Alumno", 3)
    print(f"BT-06 (Informática / Alumno / 3 demoras previas): {caso_bt06['mensaje']}")

    titulo("9. BT-08 y PI-04 - Notificación de vencimiento")
    proximos = negocio.prestamos_por_vencer(prestamos, FECHA_DE_LA_DEMO)
    print(f"Préstamos por vencer en los próximos 2 días: {len(proximos)}")
    if not proximos.empty:
        primero = proximos.iloc[0]
        aviso = negocio.generar_notificacion_vencimiento(primero, usuarios, catalogo, "ALTO")
        print("")
        print(aviso["mensaje"])

    titulo("10. BUG-03 (abierto) - Baja de un usuario con préstamo activo")
    print(f"¿U-089 tiene préstamos activos?: {negocio.tiene_prestamos_activos(prestamos, 'U-089')}")
    baja = negocio.eliminar_usuario(usuarios, "U-089")
    print(f"Resultado de la baja: {baja['mensaje']}")
    print("El sistema permite la baja igual: defecto BUG-03, pendiente de corrección.")

    titulo("11. Métricas del modelo")
    print(f"Registros evaluados: {metricas['registros_evaluados']}")
    print(f"Accuracy: {metricas['accuracy']} | Precisión: {metricas['precision']} | Recall: {metricas['recall']}")
    print(f"Matriz de confusión: {metricas['matriz_confusion']}")


if __name__ == "__main__":
    main()
