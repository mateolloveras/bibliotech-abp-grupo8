# 4. Casos de prueba, ejecución y resultados

Se diseñaron y ejecutaron **24 casos**: 16 funcionales (CF-01 a CF-08 y BT-01 a BT-08), 4 de integración (PI-01 a PI-04) y 4 de usabilidad (PU-01 a PU-04).

Los resultados obtenidos que figuran en las tablas son las salidas reales del sistema. Se pueden reproducir con:

```bash
python scripts/demo_flujo.py        # recorre el flujo e imprime cada mensaje
python -m unittest discover -s tests -t .   # ejecuta la suite automatizada
```

La salida completa de la demo está guardada como evidencia en [`docs/evidencias/salida_demo_flujo.txt`](evidencias/salida_demo_flujo.txt).

---

## 4.1. Casos funcionales — Módulo Gestión de Usuarios (CF-01 a CF-08)

| ID | Caso de prueba | Precondición | Datos de entrada | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|---|
| **CF-01** | Crear usuario válido | Pestaña "Usuarios" abierta en la interfaz | Nombre: "Juan Pérez", Email: "jperez@ispc.edu.ar", Rol: "Estudiante" | 1. Completar los campos. 2. Click en Guardar. | El sistema registra el usuario y muestra la confirmación | Se agrega el registro con ID **U-104** y se imprime "✅ Usuario registrado con éxito" | **OK** |
| **CF-02** | Crear usuario sin campos obligatorios | Pestaña "Usuarios" activa | Nombre: "" (vacío), Email: "test@ispc.edu.ar" | 1. Dejar Nombre vacío. 2. Click en Guardar. | El sistema impide guardar y avisa el campo obligatorio | No se inserta la fila y devuelve "❌ Error: El campo Nombre es obligatorio" | **OK** |
| **CF-03** | Login con credenciales correctas | Usuario registrado en el padrón | "gino.lencina@ispc.edu.ar" / "Biblio2026*" | 1. Ingresar credenciales. 2. Presionar Ingresar. | Acceso concedido y vista según el rol | "Bienvenido Gino Lencina (Rol: Bibliotecario)" | **OK** |
| **CF-04** | Login con contraseña incorrecta | Usuario registrado en el padrón | "gino.lencina@ispc.edu.ar" / "ClaveErronea123" | 1. Ingresar los datos. 2. Presionar Ingresar. | Acceso denegado con alerta visible | "❌ Error de autenticación: credenciales inválidas" | **OK** |
| **CF-05** | Editar datos de usuario | Usuario U-104 existente | Nuevo email: "jperez_nuevo@ispc.edu.ar" | 1. Seleccionar usuario. 2. Modificar email. 3. Guardar. | Datos actualizados en la tabla de usuarios | El correo se actualiza y devuelve "✅ Datos actualizados correctamente" | **OK** |
| **CF-06** | Eliminar usuario con préstamo activo | Usuario **U-089** con un préstamo vigente | ID Usuario: U-089 | 1. Seleccionar usuario. 2. Click en Eliminar. 3. Confirmar. | Debe impedir la baja para no dejar préstamos huérfanos | **FALLA:** elimina la fila sin validar los préstamos activos (ver [BUG-03](05_reporte_de_defectos.md#bug-03)) | **FALLÓ** |
| **CF-07** | Búsqueda de usuario | Al menos un usuario cargado | Texto parcial: "Lencina" | 1. Escribir el término. 2. Click en Buscar. | El sistema filtra y lista los coincidentes | El DataFrame filtrado muestra la fila de Gino Lencina | **OK** |
| **CF-08** | Cierre de sesión | Sesión activa | Click en "Cerrar Sesión" | 1. Click en "Cerrar Sesión". | Limpia el estado de sesión y vuelve al login | Estado reiniciado (`activa = False`) y retorno al formulario de ingreso | **OK** |

## 4.2. Casos funcionales — Catálogo, reservas, reglas de negocio y modelo (BT-01 a BT-08)

| ID | Caso de prueba | Técnica | Datos de entrada | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| **BT-01** | Validación del rango de días de préstamo | Valores límite | 0, 1, 14 y 15 días | 1 y 14 se procesan; 0 y 15 se rechazan con mensaje | **Falla inicial (corregida):** en la primera corrida aceptó 15 días por usar `dias < 16`. Tras corregir a `<= 14`: 0 y 15 rechazados con "El plazo de préstamo debe ser de entre 1 y 14 días corridos" | **OK (re-test)** |
| **BT-02** | Bloqueo de reserva por mora activa | Clases de equivalencia | Usuario U-012 (Suspendido) + libro con stock | Impide la reserva y alerta la penalización | "🚫 Operación no permitida: registra una penalización activa. Acérquese a biblioteca" | **OK** |
| **BT-03** | Longitud máxima en la búsqueda por título | Valores límite | Texto de 100 caracteres y de 101 caracteres | Hasta 100 filtra; con 101 avisa sin romper la ejecución | 100 caracteres filtra normal; con 101 devuelve "⚠ El término de búsqueda supera los 100 caracteres permitidos: se truncó al máximo" | **OK** |
| **BT-04** | Validación de fecha en el alta de ejemplar | Clases de equivalencia | 15/05/2021 (válida), 31/02/2024 (inexistente), 10/12/2030 (futura) | Registra la válida y rechaza las otras dos | 15/05/2021 se registra; 31/02/2024 → "❌ Error: la fecha ingresada no existe en el calendario"; 10/12/2030 → "❌ Error: la fecha de publicación no puede ser posterior al día de hoy" | **OK** |
| **BT-05** | Restricción de edición sobre el ID de ejemplar | Caja negra | Intento de modificar `ID_Ejemplar` de L-001 | El campo queda de solo lectura, sin cambios | El cambio de ID se descarta ("⚠ El campo ID_Ejemplar es de solo lectura…") y el resto de la edición sí se aplica | **OK** |
| **BT-06** | Inferencia de probabilidad de mora desde la interfaz | Integración con PP1 | Categoría "Informática", Rol "Alumno", Demoras previas: 3 | Calcula la probabilidad y clasifica el nivel de riesgo | "Probabilidad estimada de mora: **78,7 %** - 🔴 RIESGO ALTO (Priorizar recordatorio)" | **OK** |
| **BT-07** | Reserva de un ejemplar sin stock | Clases de equivalencia | Libro L-205 (Stock = 0) | Rechaza la operación informando la falta de disponibilidad | "❌ Sin disponibilidad de ejemplares físicos para este título" | **OK** |
| **BT-08** | Generación de notificación por vencimiento | Reactiva | Préstamo próximo a vencer con la fecha en formato texto | Genera el aviso con el título y la fecha límite correcta | **Falla inicial (corregida):** mostraba `Fecha límite: None` cuando la fecha venía sin parsear (ver [BUG-02](05_reporte_de_defectos.md#bug-02)). Tras la corrección imprime la fecha en formato DD/MM/AAAA | **OK (re-test)** |

## 4.3. Pruebas de integración (PI-01 a PI-04)

**Objetivo:** comprobar que los módulos internos (controles de interfaz, lógica de negocio, DataFrames y modelo de regresión logística) interactúan correctamente de punta a punta.

| ID | Módulos implicados | Escenario | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| **PI-01** | UI ↔ lógica de filtrado ↔ DataFrame catálogo | El usuario filtra por la categoría "Informática" desde el desplegable | La función consulta el catálogo y actualiza la grilla con el stock real | Devuelve los registros coincidentes, sin duplicados y de forma instantánea | **OK** |
| **PI-02** | UI reserva ↔ lógica de préstamos ↔ DataFrame catálogo | Un alumno sin sanciones reserva un ejemplar con Stock = 1 | Se agrega el registro a `df_prestamos` y el stock baja a 0 en `df_catalogo` | Ambos DataFrames quedan sincronizados: préstamo creado con fecha de devolución vacía y stock en 0 | **OK** |
| **PI-03** | Datos ↔ pipeline Scikit-Learn ↔ interfaz de alertas | Se evalúa un lote donde una fila trae `Categoria_Libro` vacía y otra una categoría nueva | El pipeline imputa, codifica, ejecuta `predict_proba()` y muestra el semáforo de riesgo | **Falla detectada y corregida:** `ValueError: Input contains NaN` detenía la celda (ver [BUG-04](05_reporte_de_defectos.md#bug-04)). Con `SimpleImputer` + `OneHotEncoder(handle_unknown="ignore")` las tres filas devuelven probabilidad y nivel | **OK (re-test)** |
| **PI-04** | Score del modelo ↔ módulo de notificaciones | Un préstamo clasificado como riesgo alto (P ≥ 0,70) dispara el aviso preventivo | El módulo toma los datos del préstamo y el nivel de riesgo y arma el correo de alerta temprana | Se genera la notificación con destinatario, título del ejemplar, fecha límite y la leyenda de aviso anticipado | **OK** |

## 4.4. Pruebas de usabilidad (PU-01 a PU-04)

**Objetivo:** evaluar que la interfaz interactiva sea fácil de usar, entendible y operable sin que el usuario final tenga que modificar el código.

| ID | Aspecto evaluado | Actividad de prueba | Criterio de éxito | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| **PU-01** | Navegación y operabilidad | Un integrante simula ser bibliotecario: busca un libro, consulta el riesgo de mora de un alumno y registra un préstamo | Completar el flujo en menos de 2 minutos sin editar celdas de código | Flujo completado en 1 min 10 s usando solo los desplegables y botones | **OK** |
| **PU-02** | Claridad de los mensajes | Provocar un bloqueo por mora (BT-02) y un error de días fuera de rango (BT-01) | Mensajes en español que indiquen la causa, sin errores crudos de Python | Los avisos explican el motivo y qué hacer ("Acérquese a biblioteca") | **OK** |
| **PU-03** | Consistencia visual e interpretabilidad (RNF1) | Revisión de los gráficos del EDA y de los indicadores del modelo | Todos los gráficos con título, etiquetas de ejes y escala coherente | Las tres visualizaciones tienen título, ejes rotulados y valores sobre las barras | **OK** |
| **PU-04** | Accesibilidad visual básica | Verificar que las alertas no dependan solo del color | Combinación de íconos (✅, ⚠, 🚫, 🔴🟡🟢) y etiquetas de texto | Cada nivel de riesgo muestra ícono **y** etiqueta ("RIESGO ALTO"), legible en modo claro y oscuro | **OK** |

## 4.5. Resumen de la ejecución

| Grupo | Casos | OK 1.ª corrida | OK tras re-testing |
|---|---|---|---|
| Funcionales de usuarios (CF) | 8 | 7 | 7 |
| Funcionales de catálogo, reservas y modelo (BT) | 8 | 6 | 8 |
| Integración (PI) | 4 | 3 | 4 |
| Usabilidad (PU) | 4 | 4 | 4 |
| **Total** | **24** | **20 (83,3 %)** | **23 (95,8 %)** |

El único caso que sigue fallando es **CF-06**, asociado a **BUG-03**, que quedó asignado para la entrega final. Con 95,8 % de casos exitosos se supera el criterio de salida del 85 %.

## 4.6. Relación entre los casos y los tests automatizados

| Caso | Test que lo verifica | Archivo |
|---|---|---|
| CF-01 | `test_cf01_crear_usuario_valido` | [`tests/test_negocio.py`](../tests/test_negocio.py) |
| CF-02 | `test_cf02_crear_usuario_sin_campos_obligatorios` | `tests/test_negocio.py` |
| CF-03 / CF-04 | `test_cf03_login_con_credenciales_correctas`, `test_cf04_login_con_clave_incorrecta` | `tests/test_negocio.py` |
| CF-05 | `test_cf05_editar_datos_de_usuario` | `tests/test_negocio.py` |
| CF-06 | `test_cf06_eliminar_usuario_con_prestamo_activo` (marcado como `expectedFailure`) | `tests/test_negocio.py` |
| CF-07 / CF-08 | `test_cf07_busqueda_de_usuario`, `test_cf08_cierre_de_sesion` | `tests/test_negocio.py` |
| BT-01 a BT-05, BT-07, BT-08 | `test_bt01_…` a `test_bt08_…` | `tests/test_negocio.py` |
| BT-06 | `test_bt06_prediccion_de_riesgo_alto` | [`tests/test_modelo.py`](../tests/test_modelo.py) |
| PI-01 a PI-04 | `test_pi01_…` a `test_pi04_…` | [`tests/test_integracion.py`](../tests/test_integracion.py) |
| RF1 / RF2 y conclusiones del EDA | `test_rf1_…`, `test_rf2_…`, `test_conclusiones_del_eda` | [`tests/test_datos.py`](../tests/test_datos.py) |

Las pruebas de usabilidad (PU-01 a PU-04) son manuales por naturaleza: se ejecutan sobre la interfaz del notebook y se documentan con capturas.
