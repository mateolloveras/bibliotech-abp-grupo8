# 1. Alcance y objetivos del proyecto

**Instituto Superior Politécnico Córdoba (ISPC)**
Tecnicatura Superior en Ciencia de Datos e Inteligencia Artificial
Materias integradas: **Testeo de Software** y **Práctica Profesionalizante I**
Año: **2026** — Grupo N° 8

| Integrante | Rol principal en el proyecto |
|---|---|
| Mateo Lloveras | Diseño y ejecución de pruebas funcionales (CF / BT) |
| Gino Agustin Lencina | Coordinación del plan de pruebas y reporte de bugs |
| Santino Vidal Gallea | Diseño y ejecución de pruebas funcionales (CF / BT) |
| Christian Quispe | Pruebas de integración / usabilidad y ajuste del modelo |
| Pablo Francisco Elias | Pruebas de integración / usabilidad y ajuste del modelo |

**Profesores a cargo:** David Cabrera y Carolina Ahumada (Testeo de Software); Daniela Accietto y Florencia García (Práctica Profesionalizante I).

---

## 1.1. Nombre del proyecto

**BiblioTech:** desarrollo, validación de calidad e integración predictiva en un entorno interactivo para la gestión de préstamos, catálogo académico y prevención de mora bibliográfica en el ISPC durante el ciclo lectivo 2026.

## 1.2. Tipo de proyecto

Tecnológico y sociocomunitario, orientado a la comunidad educativa terciaria.

## 1.3. Problemática / necesidad

La gestión manual de préstamos de material bibliográfico físico en instituciones educativas genera demoras de atención, falta de sincronización del stock disponible y una alta tasa de morosidad (en nuestros datos, un promedio de **4 días de retraso** en las devoluciones tardías), sin alertas preventivas basadas en el historial del usuario.

De ahí salen los *pain points* que atacamos:

| # | Pain point | Cómo lo resuelve BiblioTech |
|---|---|---|
| P1 | No se sabe en tiempo real qué ejemplares están disponibles. | Catálogo con stock sincronizado con cada reserva y devolución. |
| P2 | Las reglas de préstamo (plazos, sanciones) se controlan a ojo. | Validaciones automáticas de días, mora y stock antes de confirmar. |
| P3 | La mora se detecta tarde, cuando el libro ya está vencido. | Modelo de regresión logística que estima el riesgo *antes* del vencimiento. |
| P4 | No hay información consolidada para decidir compras ni políticas. | Dashboard con EDA de categorías, sedes y tiempos de préstamo. |
| P5 | Los datos históricos tienen nulos y casos atípicos que distorsionan. | Módulo de control de calidad que separa vigentes y extraviados. |

## 1.4. Fundamentación

Elegimos esta problemática porque afecta de forma directa la disponibilidad de libros de estudio en la comunidad académica. Su potencial está en unir la lógica de gestión bibliotecaria con la Ciencia de Datos: además de validar reservas y catálogo, integramos un modelo de Regresión Logística que estima en vivo la probabilidad de mora de cada préstamo para priorizar recordatorios.

En relación con nuestro perfil profesional, el proyecto nos permite asegurar tanto la **calidad interna** (código Python estructurado, modular y sin defectos críticos en el flujo de datos) como la **calidad externa** (controles interactivos intuitivos, exactos y confiables), minimizando los costos de fallas mediante pruebas tempranas.

## 1.5. Visión

Consolidar el MVP de BiblioTech como una solución institucional ágil y auditable, reduciendo en más de un 70 % el tiempo de gestión de préstamos y disminuyendo los ejemplares demorados mediante alertas preventivas guiadas por datos.

---

## 1.6. Objetivo general

Desarrollar, validar a nivel de calidad (funcional, de integración y de usabilidad) e integrar un prototipo interactivo (MVP Beta de BiblioTech) que automatice el control de préstamos, la consulta del catálogo bibliográfico y la predicción del riesgo de mora mediante aprendizaje automático durante el ciclo lectivo 2026.

## 1.7. Objetivos específicos y metas

| ID | Objetivo específico | Meta |
|---|---|---|
| **OE1** | Permitir la gestión de usuarios, autenticación y consulta del catálogo aplicando filtros dinámicos (título, autor, categoría, ISBN) desde la interfaz interactiva. | 100 % de cobertura de diseño sobre los casos de gestión de usuarios y catálogo. |
| **OE2** | Automatizar el circuito de reserva, préstamo y alta de ejemplares validando las reglas de negocio (rango de 1 a 14 días, bloqueo por mora previa y bloqueo de edición sobre IDs). | Superar el criterio de salida del 85 % de casos de prueba exitosos y resolver el 100 % de los defectos bloqueantes o urgentes. |
| **OE3** | Integrar el modelo base de Regresión Logística con una interfaz de consumo interactiva, probando el flujo completo de punta a punta (datos → modelo/lógica → interfaz). | Sostener un desempeño del modelo superior a 0,75 de *accuracy* y tiempos de inferencia menores a 2 segundos. |

## 1.8. Entregables principales

- Módulo de autenticación y gestión de roles (estudiante, docente, bibliotecario).
- Catálogo con buscador y filtros por título, autor, categoría e ISBN.
- Flujo de reserva y préstamo con validación automática de mora previa, stock y plazos.
- Panel administrativo de altas y modificaciones de ejemplares.
- Simulador de notificaciones automáticas por correo electrónico.
- Modelo predictivo de riesgo de mora integrado al flujo de reserva.
- Dashboard con el análisis exploratorio de datos.

## 1.9. Exclusiones (fuera de alcance)

- Pasarela de pagos electrónicos para el cobro de multas: el sistema solo inhabilita temporalmente al usuario.
- Módulo de lectura digital o visualizador de e-books.
- Aplicación móvil nativa.
- Migración automatizada de fichas en papel o archivos históricos previos al año 2020.

## 1.10. Criterios de aceptación

1. El sistema permite reservar un ejemplar disponible únicamente si el usuario no posee sanciones vigentes.
2. El catálogo devuelve resultados coherentes con los filtros aplicados, sin errores de interfaz ni truncamientos indebidos.
3. Las notificaciones se generan automáticamente ante cada reserva confirmada y ante la proximidad del vencimiento del préstamo.
4. El panel administrativo refleja el stock actualizado luego de cada alta, baja o modificación de ejemplares.
5. El modelo predictivo devuelve una probabilidad y un nivel de riesgo para cada préstamo en menos de 2 segundos.

---

## 1.11. Selección de acciones

| Objetivo específico | Acciones |
|---|---|
| **OE1** Gestión de usuarios, login y consulta de catálogo. | 1. Diseño de casos de prueba (CF-01 a CF-08 y BT-03). 2. Ejecución de pruebas manuales de caja negra sobre la interfaz. |
| **OE2** Automatización de reservas, control de mora y altas de libros. | 1. Pruebas por valores límite y clases de equivalencia (BT-01 a BT-05). 2. Reporte de bugs, clasificación por severidad/prioridad y re-testing. |
| **OE3** Integración de punta a punta del modelo en el notebook interactivo. | 1. Conexión de DataFrames (Pandas), modelo (Scikit-Learn) e interfaz (ipywidgets). 2. Ejecución de pruebas de integración (PI-01 a PI-04) y usabilidad (PU-01 a PU-04). |

## 1.12. Cronograma

| | Semana 1 | Semana 2 | Semana 3 | Semana 4 |
|---|---|---|---|---|
| **OE1** Usuarios, login y catálogo | Diseño de casos (CF-01 a CF-08 y BT-03) | Pruebas manuales de caja negra | | |
| **OE2** Reservas, mora y altas | | Valores límite y clases de equivalencia (BT-01 a BT-05) | Reporte de bugs, severidad/prioridad y re-testing | |
| **OE3** Integración del modelo | | | Conexión de DataFrames, modelo e interfaz | Pruebas de integración (PI) y usabilidad (PU) |

---

## 1.13. Trazabilidad con las evidencias anteriores

| Evidencia | Qué se definió | Dónde vive hoy en el repositorio |
|---|---|---|
| Evidencia 1 | Alcance, objetivos, entregables y exclusiones de BiblioTech. | Este documento (secciones 1.6 a 1.10). |
| Evidencia 2 | Criterios de aceptación, primer plan de pruebas, 8 casos funcionales, EDA inicial y modelo base. | [03_plan_de_pruebas.md](03_plan_de_pruebas.md), [04_casos_de_prueba.md](04_casos_de_prueba.md), [06_eda_y_modelo.md](06_eda_y_modelo.md) |
| Evidencia 3 | MVP Beta integrado, 24 casos ejecutados, reporte de defectos y documentación técnica. | Todo el repositorio: [`src/`](../src), [`tests/`](../tests), [`notebooks/`](../notebooks) y [`docs/`](.) |
