# 2. Requerimientos y trazabilidad

## 2.1. Requerimientos funcionales

| ID | Requerimiento | Descripción |
|---|---|---|
| **RF1** | Carga y procesamiento de datos | El sistema debe cargar y procesar el histórico de préstamos, el padrón de usuarios y el catálogo de ejemplares para habilitar su análisis. |
| **RF2** | Análisis de calidad de datos | El sistema debe identificar valores nulos, registros duplicados e inconsistencias (préstamos vigentes y ejemplares extraviados) antes de cualquier cálculo. |
| **RF3** | Generación de estadísticas descriptivas | El sistema debe generar estadísticas de las variables numéricas y categóricas: frecuencias, promedios, medianas y tasas de mora. |
| **RF4** | Generación de visualizaciones | El sistema debe generar gráficos que permitan visualizar la distribución de las variables numéricas y categóricas. |
| **RF5** | Análisis de relaciones entre variables | El sistema debe permitir analizar la relación entre variables (categoría, sede, tipo de usuario, historial de demoras y devolución tardía). |
| **RF6** | Gestión de usuarios y autenticación | El sistema debe permitir registrar, editar, buscar y dar de baja usuarios, y autenticarlos por rol. |
| **RF7** | Consulta del catálogo | El sistema debe permitir buscar ejemplares por título, autor o ISBN y filtrar por categoría. |
| **RF8** | Circuito de reserva y préstamo | El sistema debe validar sanciones, stock y plazo (1 a 14 días) antes de confirmar una reserva, y actualizar el stock. |
| **RF9** | Alta y edición de ejemplares | El sistema debe permitir dar de alta ejemplares validando la fecha de publicación y proteger el campo ID_Ejemplar. |
| **RF10** | Notificaciones de vencimiento | El sistema debe generar avisos de devolución para los préstamos próximos a vencer. |
| **RF11** | Predicción de riesgo de mora | El sistema debe estimar la probabilidad de devolución tardía de un préstamo y clasificarla en riesgo bajo, medio o alto. |

## 2.2. Requerimientos no funcionales

| ID | Requerimiento | Cómo se cumple |
|---|---|---|
| **RNF1** | Usabilidad | Interfaz de formularios y botones (ipywidgets) con mensajes en español, íconos y gráficos rotulados. Se valida con las pruebas PU-01 a PU-04. |
| **RNF2** | Rendimiento | La carga del dataset, el entrenamiento y la inferencia se resuelven en segundos. La predicción individual se mide en las pruebas y debe tardar menos de 2 segundos. |
| **RNF3** | Confiabilidad | Reglas de negocio centralizadas en [`src/negocio.py`](../src/negocio.py) y cubiertas por los tests automatizados de [`tests/`](../tests). |
| **RNF4** | Mantenibilidad | Código separado por responsabilidad (datos, negocio, modelo, EDA, interfaz), constantes y mensajes centralizados en [`src/config.py`](../src/config.py) y versionado en GitHub. |
| **RNF5** | Compatibilidad | Ejecutable en Google Colab y en cualquier entorno con Python 3.10 o superior y las librerías de [`requirements.txt`](../requirements.txt). |

## 2.3. Matriz de trazabilidad

Cada requerimiento se puede seguir hasta el código que lo implementa y hasta el caso de prueba que lo valida.

| Requerimiento | Módulo del repositorio | Función principal | Casos de prueba |
|---|---|---|---|
| RF1 | [`src/datos.py`](../src/datos.py) | `cargar_prestamos`, `cargar_usuarios`, `cargar_catalogo` | test_rf1 |
| RF2 | [`src/datos.py`](../src/datos.py) | `controlar_calidad`, `separar_por_estado` | test_rf2, PI-03 |
| RF3 | [`src/eda.py`](../src/eda.py) | `estadisticas_numericas`, `resumen_ejecutivo` | PU-03 |
| RF4 | [`src/eda.py`](../src/eda.py) | `grafico_dias_de_prestamo`, `grafico_categorias`, `grafico_mora_por_sede` | PU-03 |
| RF5 | [`src/eda.py`](../src/eda.py) / [`src/modelo.py`](../src/modelo.py) | `tasa_de_mora_por_sede`, `importancia_de_variables` | PU-03, BT-06 |
| RF6 | [`src/negocio.py`](../src/negocio.py) | `registrar_usuario`, `editar_usuario`, `buscar_usuario`, `eliminar_usuario`, `autenticar` | CF-01 a CF-08 |
| RF7 | [`src/negocio.py`](../src/negocio.py) | `buscar_en_catalogo` | BT-03, PI-01 |
| RF8 | [`src/negocio.py`](../src/negocio.py) | `validar_dias_prestamo`, `esta_sancionado`, `hay_stock`, `registrar_reserva` | BT-01, BT-02, BT-07, PI-02 |
| RF9 | [`src/negocio.py`](../src/negocio.py) | `validar_fecha_publicacion`, `dar_de_alta_ejemplar`, `editar_ejemplar` | BT-04, BT-05 |
| RF10 | [`src/negocio.py`](../src/negocio.py) | `prestamos_por_vencer`, `generar_notificacion_vencimiento` | BT-08, PI-04 |
| RF11 | [`src/modelo.py`](../src/modelo.py) | `construir_pipeline`, `entrenar_modelo`, `predecir_riesgo` | BT-06, PI-03 |

## 2.4. Diccionario de datos

### `data/prestamos_historicos.csv`

| Columna | Tipo | Descripción |
|---|---|---|
| ID_Prestamo | texto | Identificador único del préstamo (P-001, P-002, …). |
| ID_Usuario | texto | Usuario que retiró el ejemplar (clave foránea con `usuarios.csv`). |
| ID_Ejemplar | texto | Ejemplar prestado (clave foránea con `catalogo.csv`). |
| Tipo_Usuario | texto | Alumno o Docente. |
| Categoria_Libro | texto | Categoría temática del ejemplar. |
| Sede | texto | Sede donde se realizó el préstamo. |
| Fecha_Prestamo | fecha (DD/MM/AAAA) | Fecha de retiro. |
| Fecha_Devolucion_Pactada | fecha (DD/MM/AAAA) | Fecha límite comprometida. |
| Fecha_Devolucion_Real | fecha (DD/MM/AAAA) | Fecha de devolución efectiva. **Vacía en los préstamos vigentes.** |
| Demoras_Previas | entero | Cantidad de devoluciones tardías anteriores de ese usuario. |

### `data/usuarios.csv`

| Columna | Tipo | Descripción |
|---|---|---|
| ID_Usuario | texto | Identificador único (U-001 a U-103). |
| Nombre | texto | Nombre y apellido. |
| Email | texto | Correo institucional, usado como nombre de usuario. |
| Rol | texto | Estudiante, Docente o Bibliotecario. |
| Tipo_Usuario | texto | Alumno o Docente (variable que consume el modelo). |
| Sede | texto | Sede de pertenencia. |
| Estado | texto | Activo o Suspendido (con mora). |
| Hash_Clave | texto | SHA-256 de la contraseña. No se guardan contraseñas en texto plano. |

### `data/catalogo.csv`

| Columna | Tipo | Descripción |
|---|---|---|
| ID_Ejemplar | texto | Identificador único (L-001 a L-205). Campo protegido de edición. |
| Titulo | texto | Título del ejemplar. |
| Autor | texto | Autor principal. |
| ISBN | texto | Código ISBN. |
| Categoria_Libro | texto | Categoría temática. |
| Sede | texto | Sede donde está físicamente el ejemplar. |
| Stock | entero | Cantidad de copias disponibles. |
| Fecha_Publicacion | fecha (DD/MM/AAAA) | Fecha de publicación de la edición. |

> **Sobre los datos:** el dataset es un conjunto sintético reproducible que generamos con [`scripts/generar_datos.py`](../scripts/generar_datos.py) a partir del comportamiento relevado del histórico de préstamos. Se usa así porque los datos reales de la biblioteca contienen información personal de alumnos que no podemos publicar en un repositorio abierto.
