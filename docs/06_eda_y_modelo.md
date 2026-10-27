# 6. Análisis exploratorio de datos y modelo predictivo

Esta parte corresponde a **Práctica Profesionalizante I**. Todo lo que está acá se puede reproducir ejecutando el notebook [`notebooks/BiblioTech_MVP.ipynb`](../notebooks/BiblioTech_MVP.ipynb) o los módulos [`src/eda.py`](../src/eda.py) y [`src/modelo.py`](../src/modelo.py).

## 6.1. Dataset

Trabajamos sobre un extracto del histórico de préstamos de los últimos doce meses (904 registros) con las variables: ID de préstamo, ID de usuario, ID de ejemplar, tipo de usuario (alumno o docente), categoría del libro, sede, fecha de préstamo, fecha de devolución pactada, fecha de devolución real y cantidad de demoras previas del usuario.

| Indicador | Valor |
|---|---|
| Préstamos registrados | 904 |
| Préstamos vigentes (sin devolución real) | 56 |
| Ejemplares extraviados (demora mayor a 90 días) | 9 |
| Préstamos cerrados usados para el análisis y el modelo | 839 |
| Devoluciones tardías sobre préstamos cerrados | 296 (35,3 %) |
| **Promedio de días de demora en devoluciones tardías** | **4,0 días** |

## 6.2. Control de calidad de datos (RF2)

| Control | Resultado |
|---|---|
| Registros duplicados | 0 |
| Columnas con valores nulos | Únicamente `Fecha_Devolucion_Real` |
| Valores fuera de rango en `Demoras_Previas` | 0 |
| Integridad de claves (usuario y ejemplar existen) | Correcta |

**Decisiones que tomamos frente a los valores faltantes y atípicos:**

1. **Valores nulos (`Fecha_Devolucion_Real` vacía).** Son los préstamos que todavía están vigentes. Decidimos **excluirlos** del cálculo del promedio de demora y del entrenamiento del modelo, en lugar de imputarlos: inventar una fecha de devolución distorsionaría la métrica y le enseñaría al modelo un comportamiento que todavía no ocurrió.
2. **Valores atípicos (demoras mayores a 90 días).** Detectamos 9 casos. Los **documentamos aparte** como ejemplares reportados perdidos, porque no representan una demora real de devolución sino una baja del ejemplar. Si los dejáramos dentro, el promedio de demora saltaría de 4 días a más de 5, y la biblioteca tomaría decisiones sobre un número que no describe a nadie.
3. **Categorías vacías en la inferencia.** Durante la integración apareció el BUG-04: un registro con `Categoria_Libro` en NaN rompía el pipeline. Se resolvió imputando la categoría por defecto "General" dentro del propio `Pipeline`, para que la limpieza viaje junto con el modelo y no dependa de que alguien se acuerde de limpiar antes.

## 6.3. Estadística descriptiva y visualizaciones (RF3, RF4 y RF5)

**Hallazgos principales:**

- Las categorías más solicitadas son **Informática** y **Ciencias Sociales**, que juntas explican casi la mitad de los préstamos.
- La sede **Cosquín** concentra la mayor cantidad de préstamos y también **la mayor tasa de mora**, lo que la convierte en la sede donde más conviene activar los recordatorios preventivos.
- El plazo más elegido es el de 7 días, seguido por el de 14.
- Los usuarios con demoras previas vuelven a demorarse: es la variable que más pesa en el modelo.

Los tres gráficos del EDA están versionados en [`docs/evidencias/`](evidencias):

| Gráfico | Archivo | Qué muestra |
|---|---|---|
| Histograma de días de préstamo | `eda_01_histograma_dias_prestamo.png` | Distribución de los plazos solicitados. |
| Categorías más solicitadas | `eda_02_categorias_mas_solicitadas.png` | Ranking de categorías por cantidad de préstamos. |
| Tasa de mora por sede | `eda_03_mora_por_sede.png` | Porcentaje de devoluciones tardías en cada sede. |

Se regeneran con:

```bash
python scripts/generar_evidencias.py
```

## 6.4. Modelo base

**Pain point priorizado:** la falta de control estricto sobre los plazos de devolución (P3 del [documento de alcance](01_alcance_y_objetivos.md)).

**Modelo:** regresión logística que estima la probabilidad de que un préstamo termine con devolución tardía.

| Elemento | Definición |
|---|---|
| Variable objetivo | `Devolucion_Tardia` (1 si la devolución real fue posterior a la pactada) |
| Variables predictoras | `Categoria_Libro`, `Tipo_Usuario`, `Sede`, `Demoras_Previas` |
| Preprocesamiento | `SimpleImputer` + `OneHotEncoder(handle_unknown="ignore")` para las categóricas; `SimpleImputer(median)` + `StandardScaler` para la numérica |
| Algoritmo | `LogisticRegression(max_iter=1000)` |
| División de datos | 75 % entrenamiento / 25 % prueba, estratificada |

Todo el preprocesamiento vive dentro de un `Pipeline` de Scikit-Learn, así que entrenamiento e inferencia aplican exactamente las mismas transformaciones.

### Métricas obtenidas

| Métrica | Valor |
|---|---|
| Accuracy | **0,78** |
| Precisión | **0,71** |
| Recall | **0,65** |

Matriz de confusión sobre el conjunto de prueba (210 préstamos):

| | Predicho: a tiempo | Predicho: tardío |
|---|---|---|
| **Real: a tiempo** | 116 | 20 |
| **Real: tardío** | 26 | 48 |

**Cómo leemos estos números:** de cada 100 préstamos que el sistema marca como riesgosos, 71 efectivamente terminan con demora (precisión), y el modelo logra detectar 65 de cada 100 préstamos que realmente se van a demorar (recall). Para el caso de uso esto es razonable: el costo de un falso positivo es mandar un recordatorio de más, mientras que el costo de un falso negativo es un libro que no vuelve. Por eso, para la entrega final queremos subir el recall aunque la precisión baje un poco.

### Clasificación del riesgo

| Nivel | Probabilidad | Acción |
|---|---|---|
| 🟢 Riesgo bajo | menor a 0,40 | Sin acción preventiva |
| 🟡 Riesgo medio | entre 0,40 y 0,69 | Seguimiento habitual |
| 🔴 Riesgo alto | 0,70 o más | Priorizar recordatorio temprano |

## 6.5. Limitaciones conocidas

- **Muestra reducida:** 839 préstamos cerrados. Las métricas son preliminares y pueden moverse al ampliar el histórico.
- **Persistencia efímera en Colab:** los usuarios y préstamos que se cargan durante la demo viven en memoria; si se reinicia el entorno se pierden, salvo que se exporten a CSV.
- **El modelo no usa renovaciones:** la variable "cantidad de renovaciones" todavía no está en el dataset y creemos que explica parte de la demora.
- **Dataset sintético:** el histórico publicado es un conjunto reproducible generado con [`scripts/generar_datos.py`](../scripts/generar_datos.py), porque los datos reales contienen información personal de alumnos.

## 6.6. Próximos pasos

1. Ampliar la muestra de datos e incorporar la variable de renovaciones de préstamo.
2. Comparar la regresión logística contra un árbol de decisión simple, mirando especialmente el recall.
3. Resolver BUG-03 implementando la baja lógica de usuarios.
4. Exportar automáticamente a CSV los movimientos de la sesión para que el prototipo deje de ser efímero.
