import pandas as pd

from src import config

COLUMNAS_FECHA = [
    "Fecha_Prestamo",
    "Fecha_Devolucion_Pactada",
    "Fecha_Devolucion_Real",
]


def convertir_fechas(df, columnas=COLUMNAS_FECHA):
    datos = df.copy()
    for columna in columnas:
        if columna in datos.columns:
            datos[columna] = pd.to_datetime(
                datos[columna], format=config.FORMATO_FECHA, errors="coerce"
            )
    return datos


def cargar_prestamos(ruta=None):
    ruta = ruta or config.ARCHIVO_PRESTAMOS
    return convertir_fechas(pd.read_csv(ruta))


def cargar_usuarios(ruta=None):
    ruta = ruta or config.ARCHIVO_USUARIOS
    return pd.read_csv(ruta)


def cargar_catalogo(ruta=None):
    ruta = ruta or config.ARCHIVO_CATALOGO
    datos = pd.read_csv(ruta)
    datos["Fecha_Publicacion"] = pd.to_datetime(
        datos["Fecha_Publicacion"], format=config.FORMATO_FECHA, errors="coerce"
    )
    return datos


def cargar_todo():
    return cargar_prestamos(), cargar_usuarios(), cargar_catalogo()


def controlar_calidad(df, nombre="dataset"):
    nulos = df.isna().sum()
    return {
        "nombre": nombre,
        "filas": len(df),
        "columnas": len(df.columns),
        "duplicados": int(df.duplicated().sum()),
        "columnas_con_nulos": {
            columna: int(cantidad) for columna, cantidad in nulos.items() if cantidad > 0
        },
        "total_nulos": int(nulos.sum()),
    }


def informe_de_calidad(df, nombre="dataset"):
    resumen = controlar_calidad(df, nombre)
    lineas = [
        f"Control de calidad de datos: {resumen['nombre']}",
        f"  Registros: {resumen['filas']} | Variables: {resumen['columnas']}",
        f"  Registros duplicados: {resumen['duplicados']}",
    ]
    if resumen["columnas_con_nulos"]:
        lineas.append("  Valores nulos detectados:")
        for columna, cantidad in resumen["columnas_con_nulos"].items():
            porcentaje = cantidad / resumen["filas"] * 100
            lineas.append(f"    - {columna}: {cantidad} ({porcentaje:.1f}%)")
    else:
        lineas.append("  Valores nulos detectados: ninguno")
    return "\n".join(lineas)


def preparar_prestamos(df):
    datos = convertir_fechas(df)
    datos["Dias_Pactados"] = (
        datos["Fecha_Devolucion_Pactada"] - datos["Fecha_Prestamo"]
    ).dt.days
    datos["Dias_Demora"] = (
        datos["Fecha_Devolucion_Real"] - datos["Fecha_Devolucion_Pactada"]
    ).dt.days
    datos["Prestamo_Vigente"] = datos["Fecha_Devolucion_Real"].isna()
    datos["Ejemplar_Extraviado"] = (
        datos["Dias_Demora"] > config.DIAS_PARA_CONSIDERAR_EXTRAVIO
    ).fillna(False)
    datos[config.COLUMNA_OBJETIVO] = (datos["Dias_Demora"] > 0).astype("Int64")
    datos.loc[datos["Prestamo_Vigente"], config.COLUMNA_OBJETIVO] = pd.NA
    datos["Estado_Prestamo"] = "Devuelto en término"
    datos.loc[datos["Dias_Demora"] > 0, "Estado_Prestamo"] = "Devuelto con demora"
    datos.loc[datos["Ejemplar_Extraviado"], "Estado_Prestamo"] = "Extraviado"
    datos.loc[datos["Prestamo_Vigente"], "Estado_Prestamo"] = "Vigente"
    return datos


def separar_por_estado(df):
    datos = preparar_prestamos(df)
    vigentes = datos[datos["Prestamo_Vigente"]]
    extraviados = datos[datos["Ejemplar_Extraviado"]]
    cerrados = datos[~datos["Prestamo_Vigente"] & ~datos["Ejemplar_Extraviado"]]
    return cerrados, vigentes, extraviados


def datos_para_modelo(df):
    cerrados, _, _ = separar_por_estado(df)
    columnas = (
        config.COLUMNAS_CATEGORICAS
        + config.COLUMNAS_NUMERICAS
        + [config.COLUMNA_OBJETIVO]
    )
    modelo = cerrados[columnas].copy()
    modelo[config.COLUMNA_OBJETIVO] = modelo[config.COLUMNA_OBJETIVO].astype(int)
    return modelo
