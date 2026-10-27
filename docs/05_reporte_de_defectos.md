# 5. Reporte de defectos (bugs)

Siguiendo la teoría de la cátedra —un **error** humano al programar introduce un **defecto** (bug) en el código que, al ejecutarse, produce un **fallo** observable—, registramos los 4 defectos detectados durante el testeo del prototipo, clasificados por **severidad** (impacto técnico) y **prioridad** (urgencia para el negocio).

## 5.1. Tabla resumen

| ID | Caso asociado | Resumen | Severidad | Prioridad | Estado | ¿Solucionado? |
|---|---|---|---|---|---|---|
| **BUG-01** | BT-01 | La validación de reserva permite 15 días de préstamo, superando el máximo de 14. | Mayor | Urgente | Cerrado | **Sí**, verificado en re-testing |
| **BUG-02** | BT-08 | El generador de notificaciones imprime `Fecha límite: None` cuando la fecha no fue convertida a `datetime`. | Media | Alta | Cerrado | **Sí**, con `pd.to_datetime` |
| **BUG-03** | CF-06 | "Eliminar usuario" borra al usuario del DataFrame sin verificar si tiene préstamos activos. | Crítica | Media | Asignado | **No**, pendiente de baja lógica |
| **BUG-04** | PI-03 | El pipeline del modelo arroja `ValueError` cuando llega un registro con `Categoria_Libro` vacía (NaN). | Crítica | Urgente | Cerrado | **Sí**, con `SimpleImputer` |

**Severidad vs. prioridad:** BUG-03 es el caso más interesante de la tabla. Es de severidad **crítica** porque rompe la integridad referencial entre usuarios y préstamos (quedan préstamos huérfanos), pero su prioridad es **media** porque existe una solución de contorno: en lugar de eliminar al usuario, el bibliotecario le cambia el estado a Suspendido. Al revés pasa con BUG-02: la severidad es media (el sistema no se cae) pero la prioridad es alta, porque el correo que recibe el alumno queda sin fecha y pierde todo sentido como recordatorio.

---

## 5.2. Detalle de los defectos

### BUG-01

| Campo | Detalle |
|---|---|
| **Caso de prueba asociado** | BT-01 (Validación de rango de días de préstamo) |
| **Reporter** | Mateo Lloveras / Santino Vidal Gallea |
| **Versión / ambiente** | Notebook MVP Beta v1.0 - Google Colab (Python 3, Chrome) |
| **Componente** | `registrar_reserva()` — validación del input numérico `dias_solicitados` |
| **Severidad** | Mayor |
| **Prioridad** | Urgente |

**Resumen:** Módulo Reservas - Días de préstamo - Permite reservar por 15 días cuando el tope reglamentario es 14.

**Pasos para reproducir:**

1. Ejecutar la celda interactiva de Reservas con un usuario activo sin mora.
2. Seleccionar un libro con stock disponible.
3. Ingresar el valor límite 15 en el campo "Días de Préstamo" y presionar "Confirmar Reserva".

**Falla (resultado obtenido):** el sistema procesa la reserva por 15 días como válida, porque el condicional estaba escrito como `if 1 <= dias < 16:` en lugar de `if 1 <= dias <= 14:`.

**Resultado esperado:** el sistema debe rechazar el valor 15 e imprimir "El plazo de préstamo debe ser de entre 1 y 14 días corridos".

**Estado / solución:** **Cerrado.** Se corrigió el operador relacional en la función `validar_dias_prestamo()` de [`src/negocio.py`](../src/negocio.py) y se volvió a ejecutar BT-01 con los cuatro valores límite (0, 1, 14 y 15), pasando con éxito. La corrección quedó protegida con el test `test_bt01_rango_de_dias_de_prestamo`.

---

### BUG-02

| Campo | Detalle |
|---|---|
| **Caso de prueba asociado** | BT-08 (Generación de notificación por vencimiento) |
| **Reporter** | Gino Agustin Lencina |
| **Versión / ambiente** | Notebook MVP Beta v1.0 - Google Colab |
| **Componente** | `generar_notificacion_vencimiento()` — armado del cuerpo del correo |
| **Severidad** | Media |
| **Prioridad** | Alta |

**Resumen:** Módulo Notificaciones - El aviso de vencimiento muestra `Fecha límite: None`.

**Pasos para reproducir:**

1. Tomar un préstamo cuya `Fecha_Devolucion_Pactada` venga como texto desde el CSV (sin conversión previa).
2. Ejecutar el verificador de vencimientos y generar el aviso.

**Falla (resultado obtenido):** el texto se armaba con `fecha.strftime(...)` sobre un string, por lo que el formateo devolvía `None` y el correo llegaba sin fecha de devolución.

**Resultado esperado:** el aviso debe mostrar la fecha límite formateada como DD/MM/AAAA.

**Estado / solución:** **Cerrado.** Se convierte la fecha con `pd.to_datetime(..., errors="coerce")` antes de formatearla y se agregó una validación que corta la generación si la fecha es inválida. Verificado con `test_bt08_notificacion_con_fecha_sin_convertir`, que además comprueba que el texto no contenga la palabra `None`.

---

### BUG-03

| Campo | Detalle |
|---|---|
| **Caso de prueba asociado** | CF-06 (Eliminar usuario) |
| **Reporter** | Gino Agustin Lencina |
| **Versión / ambiente** | Notebook MVP Beta v1.0 - Google Colab |
| **Componente** | Módulo Gestión de Usuarios — `eliminar_usuario(df_usuarios, id_usuario)` |
| **Severidad** | Crítica (afecta la integridad referencial entre usuarios y préstamos) |
| **Prioridad** | Media (existe solución de contorno: cambiar el estado del usuario) |

**Resumen:** Gestión de Usuarios - Baja de usuario - Elimina usuarios que tienen préstamos vigentes sin devolver.

**Pasos para reproducir:**

1. En la sección Gestión de Usuarios, seleccionar el usuario **U-089**, que figura con un préstamo activo en `df_prestamos`.
2. Ejecutar la acción "Eliminar Usuario".

**Falla (resultado obtenido):** se ejecuta el filtrado/`drop` sobre el DataFrame de usuarios sin consultar `df_prestamos`, por lo que el préstamo vigente queda huérfano y el ejemplar no se puede reclamar.

**Resultado esperado:** el sistema debe verificar primero si existen préstamos activos para ese ID_Usuario y, de existir, impedir la baja mostrando un mensaje de advertencia.

**Estado / solución:** **Asignado (no solucionado).** Queda documentado para resolverse con baja lógica (`Estado = 'Inactivo'`) y una validación cruzada antes de la entrega final del ABP. La función de verificación `tiene_prestamos_activos()` ya está implementada en [`src/negocio.py`](../src/negocio.py): falta llamarla desde `eliminar_usuario()`. El caso CF-06 está en la suite como `expectedFailure`, de modo que el defecto queda visible en cada ejecución de los tests.

**Corrección prevista:**

```
resultado = negocio.tiene_prestamos_activos(df_prestamos, id_usuario)
si resultado es verdadero -> rechazar la baja y avisar al bibliotecario
si no -> marcar Estado = 'Inactivo' en lugar de borrar la fila
```

---

### BUG-04

| Campo | Detalle |
|---|---|
| **Caso de prueba asociado** | PI-03 (Integración Datos ↔ Modelo ↔ Interfaz) |
| **Reporter** | Christian Quispe / Pablo Francisco Elias |
| **Versión / ambiente** | Notebook MVP Beta v1.0 - Google Colab (scikit-learn) |
| **Componente** | `predecir_riesgo()` / pipeline de preprocesamiento |
| **Severidad** | Crítica |
| **Prioridad** | Urgente |

**Resumen:** Integración del modelo predictivo - `ValueError` al evaluar registros con la categoría del libro vacía.

**Pasos para reproducir:**

1. Cargar un lote de prueba donde el campo `Categoria_Libro` esté vacío (NaN o None).
2. Ejecutar el botón de predicción de mora.

**Falla (resultado obtenido):** la celda arroja `ValueError: Input contains NaN` al transformar las variables de entrada y se corta la ejecución de toda la interfaz.

**Resultado esperado:** el pipeline debe imputar automáticamente la categoría por defecto "General" y devolver la probabilidad de mora sin interrumpir la interfaz.

**Estado / solución:** **Cerrado.** Se integraron `SimpleImputer(strategy="constant", fill_value="General")` y `OneHotEncoder(handle_unknown="ignore")` dentro del `Pipeline` de [`src/modelo.py`](../src/modelo.py), de modo que tanto los nulos como las categorías nunca vistas se procesan sin error. Verificado con `test_pi03_el_modelo_tolera_categorias_nulas` y con `test_el_pipeline_incluye_imputacion_y_codificacion`.

---

## 5.3. Ciclo de vida de los defectos

```
Nuevo  ->  Asignado  ->  En corrección  ->  Resuelto  ->  Re-test  ->  Cerrado
                                                            |
                                                            +-> Reabierto (si el re-test falla)
```

| Defecto | Nuevo | Asignado | Resuelto | Re-test | Cerrado |
|---|---|---|---|---|---|
| BUG-01 | ✔ | ✔ | ✔ | ✔ OK | ✔ |
| BUG-02 | ✔ | ✔ | ✔ | ✔ OK | ✔ |
| BUG-03 | ✔ | ✔ | — | — | — |
| BUG-04 | ✔ | ✔ | ✔ | ✔ OK | ✔ |

## 5.4. Lecciones aprendidas

1. **Los valores límite encuentran errores reales.** BUG-01 es el error clásico de `<` en lugar de `<=`: nunca aparece probando con 7 días, solo probando con 14 y 15.
2. **Integrar no es sumar módulos.** BUG-04 no se detecta probando el modelo por separado ni la interfaz por separado: aparece cuando un dato sucio del CSV llega hasta el pipeline.
3. **Severidad no es prioridad.** BUG-03 es crítico pero se puede convivir con él gracias a una solución de contorno; eso nos permitió priorizar BUG-01 y BUG-04 para esta entrega.
4. **Un test que falla a propósito también es documentación.** Dejar CF-06 como `expectedFailure` hace que el defecto abierto se vea en cada corrida en lugar de quedar escondido en un informe.
