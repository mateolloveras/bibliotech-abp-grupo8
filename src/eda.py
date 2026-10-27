import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src import config, datos

PALETA = "crest"


def aplicar_estilo():
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (8, 4.5)
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.titleweight"] = "bold"


def estadisticas_numericas(df):
    preparados = datos.preparar_prestamos(df)
    columnas = ["Dias_Pactados", "Dias_Demora", "Demoras_Previas"]
    return preparados[columnas].describe().round(2)


def estadisticas_categoricas(df):
    preparados = datos.preparar_prestamos(df)
    resumen = {}
    for columna in ["Categoria_Libro", "Sede", "Tipo_Usuario", "Estado_Prestamo"]:
        frecuencias = preparados[columna].value_counts()
        porcentajes = (frecuencias / len(preparados) * 100).round(1)
        resumen[columna] = pd.DataFrame(
            {"Cantidad": frecuencias, "Porcentaje": porcentajes}
        )
    return resumen


def promedio_de_demora(df):
    cerrados, _, _ = datos.separar_por_estado(df)
    tardios = cerrados[cerrados["Dias_Demora"] > 0]
    return round(float(tardios["Dias_Demora"].mean()), 1)


def tasa_de_mora_por_sede(df):
    cerrados, _, _ = datos.separar_por_estado(df)
    agrupado = cerrados.groupby("Sede").agg(
        Prestamos=("ID_Prestamo", "count"),
        Devoluciones_Tardias=(config.COLUMNA_OBJETIVO, "sum"),
    )
    agrupado["Tasa_Mora"] = (
        agrupado["Devoluciones_Tardias"] / agrupado["Prestamos"] * 100
    ).round(1)
    return agrupado.sort_values("Tasa_Mora", ascending=False)


def categorias_mas_solicitadas(df, cantidad=8):
    preparados = datos.preparar_prestamos(df)
    return preparados["Categoria_Libro"].value_counts().head(cantidad)


def resumen_ejecutivo(df):
    cerrados, vigentes, extraviados = datos.separar_por_estado(df)
    ranking = categorias_mas_solicitadas(df)
    sedes = datos.preparar_prestamos(df)["Sede"].value_counts()
    mora = tasa_de_mora_por_sede(df)
    tardios = int(cerrados[config.COLUMNA_OBJETIVO].sum())
    return {
        "total_prestamos": len(df),
        "prestamos_cerrados": len(cerrados),
        "prestamos_vigentes": len(vigentes),
        "ejemplares_extraviados": len(extraviados),
        "devoluciones_tardias": tardios,
        "porcentaje_mora": round(tardios / len(cerrados) * 100, 1),
        "promedio_dias_demora": promedio_de_demora(df),
        "categoria_top": ranking.index[0],
        "segunda_categoria": ranking.index[1],
        "sede_con_mas_prestamos": sedes.index[0],
        "sede_con_mas_mora": mora.index[0],
    }


def imprimir_resumen(df):
    resumen = resumen_ejecutivo(df)
    lineas = [
        "Resumen del histórico de préstamos (últimos 12 meses)",
        f"  Préstamos registrados: {resumen['total_prestamos']}",
        f"  Préstamos vigentes (sin devolución real): {resumen['prestamos_vigentes']}",
        f"  Ejemplares reportados como extraviados (demora > 90 días): {resumen['ejemplares_extraviados']}",
        f"  Devoluciones tardías sobre préstamos cerrados: {resumen['devoluciones_tardias']} ({resumen['porcentaje_mora']}%)",
        f"  Promedio de días de demora en devoluciones tardías: {resumen['promedio_dias_demora']} días",
        f"  Categorías más solicitadas: {resumen['categoria_top']} y {resumen['segunda_categoria']}",
        f"  Sede con más préstamos: {resumen['sede_con_mas_prestamos']}",
        f"  Sede con mayor tasa de mora: {resumen['sede_con_mas_mora']}",
    ]
    return "\n".join(lineas)


def grafico_dias_de_prestamo(df, ruta=None, mostrar=False):
    aplicar_estilo()
    preparados = datos.preparar_prestamos(df)
    figura, ejes = plt.subplots()
    sns.histplot(data=preparados, x="Dias_Pactados", bins=14, color="#2a6f97", ax=ejes)
    ejes.set_title("Distribución de días de préstamo solicitados")
    ejes.set_xlabel("Días de préstamo pactados")
    ejes.set_ylabel("Cantidad de préstamos")
    return _cerrar(figura, ruta, mostrar)


def grafico_categorias(df, ruta=None, mostrar=False):
    aplicar_estilo()
    ranking = categorias_mas_solicitadas(df)
    figura, ejes = plt.subplots()
    sns.barplot(x=ranking.values, y=ranking.index, hue=ranking.index, palette=PALETA, legend=False, ax=ejes)
    ejes.set_title("Categorías más solicitadas")
    ejes.set_xlabel("Cantidad de préstamos")
    ejes.set_ylabel("Categoría del libro")
    for contenedor in ejes.containers:
        ejes.bar_label(contenedor, padding=3, fontsize=9)
    return _cerrar(figura, ruta, mostrar)


def grafico_mora_por_sede(df, ruta=None, mostrar=False):
    aplicar_estilo()
    mora = tasa_de_mora_por_sede(df).reset_index()
    figura, ejes = plt.subplots()
    sns.barplot(data=mora, x="Sede", y="Tasa_Mora", hue="Sede", palette="flare", legend=False, ax=ejes)
    ejes.set_title("Tasa de devoluciones tardías por sede")
    ejes.set_xlabel("Sede")
    ejes.set_ylabel("Devoluciones tardías (%)")
    for contenedor in ejes.containers:
        ejes.bar_label(contenedor, fmt="%.1f%%", padding=3, fontsize=9)
    return _cerrar(figura, ruta, mostrar)


def _cerrar(figura, ruta, mostrar):
    figura.tight_layout()
    if ruta is not None:
        figura.savefig(ruta, dpi=120)
    if mostrar:
        plt.show()
    else:
        plt.close(figura)
    return figura


def generar_evidencias_visuales(df, carpeta=None):
    carpeta = carpeta or config.CARPETA_EVIDENCIAS
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = {
        "histograma_dias_prestamo": carpeta / "eda_01_histograma_dias_prestamo.png",
        "categorias_mas_solicitadas": carpeta / "eda_02_categorias_mas_solicitadas.png",
        "mora_por_sede": carpeta / "eda_03_mora_por_sede.png",
    }
    grafico_dias_de_prestamo(df, ruta=rutas["histograma_dias_prestamo"])
    grafico_categorias(df, ruta=rutas["categorias_mas_solicitadas"])
    grafico_mora_por_sede(df, ruta=rutas["mora_por_sede"])
    return rutas
