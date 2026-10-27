import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import seaborn as sns

from src import config, datos, eda, modelo


def grafico_matriz_de_confusion(metricas, ruta):
    eda.aplicar_estilo()
    matriz = metricas["matriz_confusion"]
    figura, ejes = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(
        matriz,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["A tiempo", "Tardío"],
        yticklabels=["A tiempo", "Tardío"],
        ax=ejes,
    )
    ejes.set_title("Matriz de confusión del modelo de riesgo de mora")
    ejes.set_xlabel("Predicción del modelo")
    ejes.set_ylabel("Valor real")
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
    plt.close(figura)


def main():
    prestamos = datos.cargar_prestamos()
    config.CARPETA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    rutas = eda.generar_evidencias_visuales(prestamos)
    entrenado, metricas = modelo.entrenar_modelo(prestamos)
    ruta_matriz = config.CARPETA_EVIDENCIAS / "modelo_01_matriz_de_confusion.png"
    grafico_matriz_de_confusion(metricas, ruta_matriz)

    print(eda.imprimir_resumen(prestamos))
    print("")
    print(f"Métricas del modelo: {metricas}")
    print("")
    for ruta in list(rutas.values()) + [ruta_matriz]:
        print(f"Evidencia generada: {ruta}")


if __name__ == "__main__":
    main()
