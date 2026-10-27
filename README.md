# BiblioTech — MVP Beta

Sistema de gestión de préstamos bibliotecarios con predicción de riesgo de mora.
Proyecto ABP que integra **Testeo de Software** y **Práctica Profesionalizante I**.

**Instituto Superior Politécnico Córdoba (ISPC)** · Tecnicatura Superior en Ciencia de Datos e Inteligencia Artificial · Año 2026 · **Grupo N° 8**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mateolloveras/bibliotech-abp-grupo8/blob/main/notebooks/BiblioTech_MVP.ipynb)

| Integrante | Rol en el proyecto |
|---|---|
| Mateo Lloveras | Diseño y ejecución de pruebas funcionales |
| Gino Agustin Lencina | Coordinación del plan de pruebas y reporte de bugs |
| Santino Vidal Gallea | Diseño y ejecución de pruebas funcionales |
| Christian Quispe | Pruebas de integración / usabilidad y modelo |
| Pablo Francisco Elias | Pruebas de integración / usabilidad y modelo |

**Profesores:** David Cabrera y Carolina Ahumada (Testeo de Software) · Daniela Accietto y Florencia García (Práctica Profesionalizante I).

---

## El problema

La gestión manual de préstamos de material bibliográfico genera demoras de atención, falta de sincronización del stock y una alta tasa de morosidad. En el histórico analizado, las devoluciones tardías llegan en promedio **4 días** después de la fecha pactada y no existe ninguna alerta preventiva basada en el historial del usuario.

**BiblioTech** automatiza el circuito de préstamo (catálogo, reservas, control de mora, altas y notificaciones) y agrega una capa de Ciencia de Datos: un modelo de regresión logística que estima la probabilidad de que un préstamo termine con demora, **antes** de que venza, para priorizar los recordatorios.

## Qué hace el sistema

| Módulo | Qué resuelve |
|---|---|
| Gestión de usuarios y login | Alta, edición, búsqueda y autenticación por rol (estudiante, docente, bibliotecario). |
| Catálogo | Búsqueda por título, autor o ISBN y filtro por categoría, con el stock real. |
| Reservas | Valida mora activa, stock y plazo (1 a 14 días), calcula la fecha de devolución y actualiza el stock. |
| Altas de ejemplares | Valida la fecha de publicación y protege el campo `ID_Ejemplar` contra edición. |
| Notificaciones | Genera el aviso de vencimiento con el título del ejemplar y la fecha límite. |
| Riesgo de mora | Devuelve probabilidad y nivel (🟢 bajo / 🟡 medio / 🔴 alto) para priorizar recordatorios. |
| Dashboard | Estadísticas descriptivas y los tres gráficos del análisis exploratorio. |

## Resultados

### Testing

| Métrica | Valor |
|---|---|
| Casos planificados y ejecutados | 24 (16 funcionales + 4 de integración + 4 de usabilidad) |
| Casos OK en la primera corrida | 20 de 24 (**83,3 %**) |
| Casos OK tras el re-testing | 23 de 24 (**95,8 %**) |
| Criterio de salida (≥ 85 % OK) | ✅ Cumplido |
| Defectos detectados / cerrados / abiertos | 4 / 3 / 1 |
| Tests automatizados en el repositorio | 36 (`python -m unittest discover -s tests -t .`) |

| Defecto | Caso | Severidad | Prioridad | Estado |
|---|---|---|---|---|
| BUG-01 — acepta 15 días de préstamo | BT-01 | Mayor | Urgente | ✅ Cerrado |
| BUG-02 — el aviso muestra `Fecha límite: None` | BT-08 | Media | Alta | ✅ Cerrado |
| BUG-03 — permite eliminar un usuario con préstamo activo | CF-06 | Crítica | Media | ⚠️ Abierto |
| BUG-04 — `ValueError` con la categoría vacía | PI-03 | Crítica | Urgente | ✅ Cerrado |

### Análisis de datos y modelo

| Indicador | Valor |
|---|---|
| Préstamos analizados (12 meses) | 904 |
| Préstamos vigentes excluidos del análisis | 56 |
| Ejemplares extraviados documentados aparte | 9 |
| Devoluciones tardías | 296 (35,3 %) |
| **Promedio de demora en devoluciones tardías** | **4,0 días** |
| Categorías más solicitadas | Informática y Ciencias Sociales |
| Sede con más préstamos y mayor mora | Cosquín |
| Modelo | Regresión logística (Pipeline de Scikit-Learn) |
| **Accuracy / Precisión / Recall** | **0,78 / 0,71 / 0,65** |

![Categorías más solicitadas](docs/evidencias/eda_02_categorias_mas_solicitadas.png)

![Tasa de mora por sede](docs/evidencias/eda_03_mora_por_sede.png)

## Cómo ejecutarlo

### Opción 1 — Google Colab (recomendada)

Abrir [`notebooks/BiblioTech_MVP.ipynb`](notebooks/BiblioTech_MVP.ipynb) con el botón **Abrir en Colab** de arriba y usar **Entorno de ejecución → Ejecutar todo**. La primera celda clona el repositorio e instala las dependencias; no hace falta editar código.

### Opción 2 — Local

```bash
git clone https://github.com/mateolloveras/bibliotech-abp-grupo8.git
cd bibliotech-abp-grupo8
pip install -r requirements.txt

python scripts/demo_flujo.py                  # recorre el flujo completo por consola
python -m unittest discover -s tests -t .     # ejecuta los 36 tests
python scripts/generar_evidencias.py          # regenera los gráficos del EDA
python scripts/generar_datos.py               # regenera los datasets (semilla fija)
```

### Datos de prueba

| Para probar | Datos |
|---|---|
| Login correcto (CF-03) | `gino.lencina@ispc.edu.ar` / `Biblio2026*` |
| Login incorrecto (CF-04) | misma cuenta con cualquier otra clave |
| Usuario con mora activa (BT-02) | `U-012` |
| Ejemplar sin stock (BT-07) | `L-205` |
| Días fuera de rango (BT-01) | 0 o 15 días |
| Usuario con préstamo activo (CF-06 / BUG-03) | `U-089` |

> Las contraseñas del entorno de prueba se guardan como hash SHA-256 en `data/usuarios.csv`.

## Estructura del repositorio

```
data/        Datasets (préstamos, usuarios, catálogo)
docs/        Documentación de ambas materias + evidencias
notebooks/   Notebook interactivo del MVP (ejecutado, con salidas)
scripts/     Generación de datos, evidencias y demo por consola
src/         Código fuente por capas (datos, negocio, modelo, EDA, interfaz)
tests/       Suite automatizada de los casos de prueba
```

## Documentación

| Documento | Contenido |
|---|---|
| [1. Alcance y objetivos](docs/01_alcance_y_objetivos.md) | Problemática, pain points, objetivos, metas, entregables, exclusiones y cronograma. |
| [2. Requerimientos](docs/02_requerimientos.md) | RF, RNF, matriz de trazabilidad y diccionario de datos. |
| [3. Plan de pruebas](docs/03_plan_de_pruebas.md) | Alcance del testing, estrategia, tareas, recursos y métricas. |
| [4. Casos de prueba](docs/04_casos_de_prueba.md) | Los 24 casos con resultado esperado, resultado obtenido y estado. |
| [5. Reporte de defectos](docs/05_reporte_de_defectos.md) | BUG-01 a BUG-04 con severidad, prioridad y ciclo de vida. |
| [6. EDA y modelo](docs/06_eda_y_modelo.md) | Control de calidad, decisiones sobre nulos y atípicos, métricas y limitaciones. |
| [7. Arquitectura y stack](docs/07_arquitectura_y_stack.md) | Capas, flujo de punta a punta y justificación de los cambios. |
| [8. Guion de la defensa](docs/08_guion_de_defensa.md) | Reparto, tiempos y secuencia exacta de la demo. |
| [9. Preguntas de la defensa](docs/09_preguntas_de_defensa.md) | Respuestas preparadas por materia. |
| [10. Anexo E-Commerce Insight](docs/10_anexo_ecommerce_insight.md) | Trabajo previo de Práctica Profesionalizante. |
| [11. Bitácora del grupo](docs/11_bitacora_del_grupo.md) | Cómo avanzamos y qué decidimos en cada semana. |

## Limitaciones conocidas

1. **BUG-03 abierto:** la baja de usuarios no valida préstamos activos. Documentado y asignado para la entrega final.
2. **Persistencia efímera:** los datos cargados durante una sesión viven en memoria; si se reinicia el entorno se pierden.
3. **Muestra reducida:** el modelo se entrena con 839 préstamos cerrados y cuatro variables; falta incorporar las renovaciones.
4. **Dataset sintético:** el histórico publicado se genera con [`scripts/generar_datos.py`](scripts/generar_datos.py) y semilla fija, porque los datos reales contienen información personal de alumnos.

## Valor añadido

Integrar ambas materias sobre el mismo prototipo nos permitió ver la diferencia entre verificar reglas aisladas y validar un sistema completo. La técnica de valores límite (BT-01) cazó un error clásico de programación en el tope de días de préstamo, y las pruebas de integración (PI-03) mostraron cómo un único dato nulo del dataset podía frenar la predicción del modelo. De esa segunda falla salió un pipeline con imputación automática mucho más robusto: el testing dejó de ser una etapa teórica y pasó a ser la garantía de calidad de nuestra solución de datos.
