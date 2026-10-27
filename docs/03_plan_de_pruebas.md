# 3. Plan de pruebas

## 3.1. Estrategia

Para esta etapa pasamos de la planificación preliminar (Evidencia 2) a la **implementación, ejecución y evaluación de criterios de salida** sobre el prototipo funcional. Usamos una estrategia combinada:

- **Analítica:** los casos salen de los requerimientos y de las reglas de negocio documentadas.
- **Reactiva:** sumamos casos nuevos a partir de los errores que fueron apareciendo durante la ejecución (por ejemplo, las fechas sin convertir del BUG-02).

Las técnicas de caja negra aplicadas son **partición en clases de equivalencia**, **análisis de valores límite** y **no enmascaramiento de errores** (un dato inválido no debe tapar al siguiente).

## 3.2. Alcance del testing

### Se va a probar

- **Funcionalidades de los requerimientos aprobados:** gestión de usuarios y autenticación (CF-01 a CF-08), catálogo, reserva de préstamos, alta de ejemplares, simulador de notificaciones y predicción de mora.
- **Validaciones de campos y restricciones funcionales:** textos (máximo 100 caracteres), numéricos (rango de 1 a 14 días), fechas (formato DD/MM/AAAA y coherencia temporal) y campos bloqueados (ID_Ejemplar).
- **Mensajes de error y confirmaciones visibles:** mensajes de éxito, alertas de sanción activa y avisos de campos obligatorios vacíos.
- **Reglas de negocio explícitas:** cálculo automático de la fecha de devolución, bloqueo de reserva a usuarios suspendidos, control de stock y clasificación del riesgo de mora según el score del modelo.
- **Pruebas de integración (optativa 1/2):** flujo de datos entre los componentes internos — formularios de la interfaz ↔ funciones de negocio en Python ↔ DataFrames ↔ pipeline de inferencia de la regresión logística.
- **Pruebas de usabilidad (optativa 2/2):** claridad de los controles interactivos, posibilidad de operar sin tocar código, comprensión de los mensajes de error y legibilidad de los gráficos y alertas.

### No se va a probar

| Fuera de alcance | Motivo / riesgo asumido |
|---|---|
| Pruebas de carga y estrés | El MVP corre en una instancia de máquina virtual por sesión de usuario en Google Colab; no hay concurrencia real que medir. |
| Pruebas de seguridad y penetración | Es un MVP en entorno controlado; se asume el riesgo y queda para la etapa de despliegue web. |
| Compatibilidad multi-navegador exhaustiva | Se prueba sobre Chrome y Firefox actualizados. |
| Pasarela de pagos y app móvil nativa | Están excluidas del alcance general del proyecto. |

### Supuestos

- Los requerimientos funcionales están documentados y aprobados.
- El entorno de ejecución cuenta con Python 3 y las librerías requeridas.
- Se dispone de datos de prueba consistentes ([`data/`](../data)).

### Criterio de salida

- 100 % de los casos planificados ejecutados.
- Al menos **85 %** de casos exitosos (OK).
- 100 % de los defectos bloqueantes o urgentes corregidos y verificados con re-testing.

## 3.3. Tareas y subtareas

### Fase 1 — Planeamiento y control

- **1.1** Actualizar el alcance del testing incorporando el módulo de gestión de usuarios y las pruebas de integración y usabilidad.
- **1.2** Distribuir responsabilidades entre los 5 integrantes (diseño, ejecución, captura de evidencias y corrección de código).

### Fase 2 — Análisis y diseño de pruebas

- **2.1** Revisar la base de pruebas: requerimientos RF y RNF, reglas de negocio y estructura de variables del modelo.
- **2.2** Seleccionar valores de entrada aplicando clases de equivalencia, valores límite y no enmascaramiento de errores.
- **2.3** Confeccionar la matriz de casos funcionales (CF-01 a CF-08 y BT-01 a BT-08), de integración (PI-01 a PI-04) y de usabilidad (PU-01 a PU-04).

### Fase 3 — Implementación y ejecución

- **3.1** Inicializar el entorno cargando el dataset histórico, entrenando el modelo base y levantando la celda de interfaz.
- **3.2** Ejecutar cada caso ingresando los datos en los widgets, comparar la salida obtenida contra el resultado esperado y tomar capturas.
- **3.3** Reportar los defectos encontrados con ID único, pasos para reproducir, severidad, prioridad y estado.

### Fase 4 — Evaluación de criterios de salida e informes

- **4.1** Ejecutar pruebas de confirmación (re-testing) y de regresión luego de aplicar las correcciones.
- **4.2** Verificar el cumplimiento del criterio de salida (≥ 85 % de casos OK) y calcular las métricas.

### Fase 5 — Cierre

- **5.1** Consolidar las tablas de resultados, el reporte de defectos y las lecciones aprendidas.

## 3.4. Recursos del testing

### Personal

| Integrante | Responsabilidad |
|---|---|
| Gino Agustin Lencina | Coordinación del plan de pruebas y reporte de bugs. |
| Mateo Lloveras | Diseño y ejecución de pruebas funcionales (CF y BT). |
| Santino Vidal Gallea | Diseño y ejecución de pruebas funcionales (CF y BT). |
| Christian Quispe | Pruebas de integración y usabilidad, ajuste del modelo. |
| Pablo Francisco Elias | Pruebas de integración y usabilidad, ajuste del modelo. |

### Hardware y ambientes

- Notebooks de los integrantes con Chrome y Firefox actualizados.
- Ambiente de pruebas en la nube: Google Colaboratory (Ubuntu Linux, Python 3) con los datos versionados en el repositorio.
- Ambiente local alternativo: Python 3.10 o superior con las dependencias de [`requirements.txt`](../requirements.txt).

### Herramientas de soporte

| Herramienta | Para qué la usamos |
|---|---|
| Google Colab + ipywidgets | Entorno de ejecución interactiva del flujo datos → modelo → interfaz. |
| `unittest` (librería estándar de Python) | Celdas y archivos de verificación automática de los casos borde ([`tests/`](../tests)). |
| Git + GitHub Actions | Versionado del código, del notebook y de los datasets, y ejecución automática de la suite en cada push (`.github/workflows/tests.yml`). |
| Trello y Google Sheets | Seguimiento de tareas, matriz de ejecución de los 24 casos y ciclo de vida de los bugs. |

## 3.5. Métricas de testing alcanzadas

| Métrica | Valor |
|---|---|
| Casos planificados | 24 (16 funcionales + 4 de integración + 4 de usabilidad) |
| Casos ejecutados | 24 (100 %) |
| Casos OK en la primera corrida | 20 de 24 (**83,3 %**) |
| Casos OK luego del re-testing | 23 de 24 (**95,8 %**) |
| Defectos detectados | 4 |
| Defectos cerrados | 3 (BUG-01, BUG-02, BUG-04) |
| Defectos abiertos | 1 (BUG-03, severidad crítica / prioridad media) |
| Criterio de salida (≥ 85 % OK) | **Cumplido** |

La primera corrida falló en BT-01 (BUG-01), BT-08 (BUG-02), PI-03 (BUG-04) y CF-06 (BUG-03). Las tres primeras se corrigieron y se volvieron a ejecutar con éxito; CF-06 sigue fallando porque BUG-03 quedó asignado para la entrega final.

> El estado de CF-06 se puede verificar en cualquier momento: en [`tests/test_negocio.py`](../tests/test_negocio.py) el caso está marcado como `expectedFailure`, así que la suite deja constancia del defecto abierto sin romper la ejecución.
