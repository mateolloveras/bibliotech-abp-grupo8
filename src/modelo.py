import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import config, datos


def construir_pipeline():
    rama_categorica = Pipeline(
        steps=[
            ("imputacion", SimpleImputer(strategy="constant", fill_value=config.CATEGORIA_POR_DEFECTO)),
            ("codificacion", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    rama_numerica = Pipeline(
        steps=[
            ("imputacion", SimpleImputer(strategy="median")),
            ("escalado", StandardScaler()),
        ]
    )
    preprocesamiento = ColumnTransformer(
        transformers=[
            ("categoricas", rama_categorica, config.COLUMNAS_CATEGORICAS),
            ("numericas", rama_numerica, config.COLUMNAS_NUMERICAS),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocesamiento", preprocesamiento),
            ("clasificador", LogisticRegression(max_iter=1000, random_state=config.SEMILLA)),
        ]
    )


def entrenar_modelo(df_prestamos, tamano_prueba=None, semilla_particion=None):
    tamano_prueba = tamano_prueba or config.PROPORCION_PRUEBA
    semilla_particion = semilla_particion if semilla_particion is not None else config.SEMILLA_PARTICION
    tabla = datos.datos_para_modelo(df_prestamos)
    variables = tabla[config.COLUMNAS_CATEGORICAS + config.COLUMNAS_NUMERICAS]
    objetivo = tabla[config.COLUMNA_OBJETIVO]
    x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
        variables,
        objetivo,
        test_size=tamano_prueba,
        random_state=semilla_particion,
        stratify=objetivo,
    )
    modelo = construir_pipeline()
    modelo.fit(x_entrenamiento, y_entrenamiento)
    metricas = evaluar_modelo(modelo, x_prueba, y_prueba)
    return modelo, metricas


def evaluar_modelo(modelo, x_prueba, y_prueba):
    predicciones = modelo.predict(x_prueba)
    return {
        "registros_evaluados": len(y_prueba),
        "accuracy": round(accuracy_score(y_prueba, predicciones), 2),
        "precision": round(precision_score(y_prueba, predicciones, zero_division=0), 2),
        "recall": round(recall_score(y_prueba, predicciones, zero_division=0), 2),
        "matriz_confusion": confusion_matrix(y_prueba, predicciones).tolist(),
    }


def clasificar_riesgo(probabilidad):
    if probabilidad >= config.UMBRAL_RIESGO_ALTO:
        return "ALTO"
    if probabilidad >= config.UMBRAL_RIESGO_MEDIO:
        return "MEDIO"
    return "BAJO"


def predecir_riesgo(modelo, categoria_libro, tipo_usuario, demoras_previas, sede="Córdoba Capital"):
    entrada = pd.DataFrame(
        [
            {
                "Categoria_Libro": categoria_libro,
                "Tipo_Usuario": tipo_usuario,
                "Sede": sede,
                "Demoras_Previas": demoras_previas,
            }
        ]
    )
    probabilidad = float(modelo.predict_proba(entrada)[0][1])
    nivel = clasificar_riesgo(probabilidad)
    return {
        "probabilidad": probabilidad,
        "porcentaje": round(probabilidad * 100, 1),
        "nivel": nivel,
        "etiqueta": config.ETIQUETAS_RIESGO[nivel],
        "mensaje": f"Probabilidad estimada de mora: {probabilidad * 100:.1f}% - {config.ETIQUETAS_RIESGO[nivel]}",
    }


def predecir_lote(modelo, df):
    entrada = df[config.COLUMNAS_CATEGORICAS + config.COLUMNAS_NUMERICAS].copy()
    probabilidades = modelo.predict_proba(entrada)[:, 1]
    resultado = df.copy()
    resultado["Probabilidad_Mora"] = probabilidades.round(4)
    resultado["Nivel_Riesgo"] = [clasificar_riesgo(valor) for valor in probabilidades]
    return resultado


def importancia_de_variables(modelo):
    preprocesamiento = modelo.named_steps["preprocesamiento"]
    nombres = list(preprocesamiento.get_feature_names_out())
    coeficientes = modelo.named_steps["clasificador"].coef_[0]
    tabla = pd.DataFrame({"Variable": nombres, "Coeficiente": coeficientes.round(3)})
    return tabla.sort_values("Coeficiente", ascending=False).reset_index(drop=True)
