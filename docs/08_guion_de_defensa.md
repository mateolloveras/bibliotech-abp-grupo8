# 8. Guion de la defensa

Presentación escrita y oral del Grupo N° 8. Duración estimada: **15 minutos de exposición + preguntas**.
La idea es que cualquiera del grupo pueda seguir este guion y que la demo salga igual todas las veces.

## 8.1. Antes de empezar (checklist)

- [ ] Abrir el notebook en Google Colab y hacer **Entorno de ejecución → Ejecutar todo** (tarda alrededor de 1 minuto).
- [ ] Verificar que la celda de pruebas haya terminado con "Fallos: 0" y "Fallos esperados: 1".
- [ ] Tener abiertas en pestañas: el repositorio en GitHub, este guion y el [reporte de defectos](05_reporte_de_defectos.md).
- [ ] Tener a mano los datos de prueba: `gino.lencina@ispc.edu.ar` / `Biblio2026*`, usuario U-012 (con mora), ejemplar L-205 (sin stock), usuario U-089 (con préstamo activo).

## 8.2. Reparto de la exposición

| Momento | Minutos | Quién | Qué dice |
|---|---|---|---|
| 1. Problema y proyecto | 2 | Pablo Elias | Qué es BiblioTech, qué problema resuelve y por qué elegimos la morosidad bibliográfica. |
| 2. Alcance del testing | 2 | Gino Lencina | Qué se prueba, qué queda afuera y por qué, y el criterio de salida del 85 %. |
| 3. Diseño y ejecución de casos | 3 | Mateo Lloveras | Las técnicas usadas y los 24 casos; muestra la tabla de resultados. |
| 4. Demo en vivo | 4 | Santino Vidal | Recorre el notebook: reserva válida, reserva bloqueada, riesgo de mora y notificación. |
| 5. Defectos encontrados | 2 | Gino Lencina | BUG-01 a BUG-04, severidad vs. prioridad y por qué BUG-03 sigue abierto. |
| 6. EDA y modelo | 2 | Christian Quispe | Decisiones sobre nulos y atípicos, métricas del modelo y próximos pasos. |
| 7. Cierre y valor añadido | 1 | Todos | Cómo se integran las dos materias. |

## 8.3. Guion detallado

### 1. Problema y proyecto (Pablo)

> "BiblioTech es la plataforma de gestión de préstamos de la biblioteca del ISPC. El problema que atacamos es concreto: la gestión manual genera demoras, no se sabe en tiempo real qué ejemplares hay disponibles y la mora se detecta cuando el libro ya está vencido. En nuestros datos, las devoluciones tardías llegan tarde en promedio **4 días**, y la sede Cosquín es la que más préstamos concentra y la que más mora tiene.
>
> Lo que agregamos en esta evidencia es que el sistema no solo controla las reglas: **anticipa** qué préstamo se va a demorar y prioriza el recordatorio."

### 2. Alcance del testing (Gino)

> "Probamos las funcionalidades de los requerimientos aprobados: usuarios y login, catálogo, reservas, altas de ejemplares, notificaciones y predicción de mora; las validaciones de campos, los mensajes de error y las reglas de negocio.
>
> Dejamos **fuera de alcance** carga y estrés, seguridad y compatibilidad multi-navegador exhaustiva, y asumimos ese riesgo porque es un MVP que corre en una instancia de Colab por usuario.
>
> Las dos pruebas optativas que sumamos son **integración** y **usabilidad**. El criterio de salida es 100 % de casos ejecutados, 85 % exitosos y 100 % de los bloqueantes corregidos."

### 3. Diseño y ejecución de casos (Mateo)

> "Diseñamos 24 casos: 16 funcionales, 4 de integración y 4 de usabilidad. Usamos **partición en clases de equivalencia** y **análisis de valores límite**.
>
> El ejemplo más claro es BT-01: el reglamento dice de 1 a 14 días, entonces probamos 0, 1, 14 y 15. Con 7 días nunca hubiéramos encontrado nada; con 15 encontramos el BUG-01.
>
> En la primera corrida pasaron 20 de 24 casos, un 83,3 %, que estaba por debajo del criterio. Después de corregir y hacer re-testing llegamos a 23 de 24, 95,8 %."

*(Mostrar la tabla de [casos de prueba](04_casos_de_prueba.md) y la de métricas.)*

### 4. Demo en vivo (Santino)

Secuencia exacta, en la interfaz del notebook:

1. **Login (CF-03):** `gino.lencina@ispc.edu.ar` / `Biblio2026*` → "Bienvenido Gino Lencina (Rol: Bibliotecario)".
2. **Catálogo (BT-03 / PI-01):** buscar "Python" y filtrar por categoría Informática → muestra los ejemplares con su stock real.
3. **Reserva válida (PI-02):** elegir un ejemplar con stock, 14 días → "✅ Reserva confirmada: devolver antes del …" y aparece el semáforo de riesgo.
4. **Reserva bloqueada por mora (BT-02):** elegir el usuario U-012 → "🚫 Operación no permitida: registra una penalización activa".
5. **Días fuera de rango (BT-01):** poner 15 días → "El plazo de préstamo debe ser de entre 1 y 14 días corridos".
6. **Riesgo de mora (BT-06):** categoría Informática, tipo Alumno, 3 demoras previas → "Probabilidad estimada de mora: 78,7 % - 🔴 RIESGO ALTO".
7. **Notificación (PI-04):** pestaña Notificaciones → se arma el correo con el título del libro y la fecha límite.

> "Fíjense que el modelo no decide si se presta el libro. Primero corren las reglas duras —mora, stock y plazo—, y recién después el modelo dice a quién conviene recordarle."

### 5. Defectos (Gino)

> "Encontramos 4 defectos. Tres están cerrados y verificados con re-testing: el tope de 15 días (BUG-01), la fecha que salía como `None` en el correo (BUG-02) y el `ValueError` del pipeline con una categoría vacía (BUG-04).
>
> Queda abierto el **BUG-03**: el sistema permite dar de baja a un usuario que tiene un libro sin devolver. Es de severidad **crítica** porque rompe la integridad entre usuarios y préstamos, pero de prioridad **media** porque hay solución de contorno: en vez de borrarlo, se lo suspende. Lo dejamos documentado y asignado para la entrega final, y está marcado en la suite de tests como fallo esperado, así no se nos pierde."

*(Si preguntan por qué no se arregló: la respuesta es prioridad y tiempo, más la existencia de la solución de contorno, no que no sepamos cómo hacerlo; la función `tiene_prestamos_activos()` ya está escrita.)*

### 6. EDA y modelo (Christian)

> "Sobre 904 préstamos de los últimos 12 meses, lo primero fue el control de calidad: no hay duplicados y los únicos nulos están en la fecha de devolución real, que son los préstamos vigentes. A esos los excluimos en vez de imputarlos, porque inventar una fecha distorsiona la métrica. También separamos 9 casos con más de 90 días de demora: son ejemplares perdidos, no demoras reales.
>
> El modelo es una regresión logística con las variables categoría, tipo de usuario, sede y demoras previas. Da **0,78 de accuracy, 0,71 de precisión y 0,65 de recall**. Lo leemos así: de cada 100 préstamos que marcamos como riesgosos, 71 terminan realmente con demora, y detectamos 65 de cada 100 que se van a demorar. Para este caso de uso preferimos subir el recall aunque baje la precisión, porque el costo de un recordatorio de más es mucho menor que el de un libro que no vuelve."

### 7. Cierre (todos)

> "Integrar las dos materias sobre el mismo prototipo nos mostró la diferencia entre verificar reglas aisladas y validar un sistema completo. Los valores límite cazaron un error clásico de programación en el tope de días, y las pruebas de integración mostraron que un solo dato nulo del dataset podía frenar la predicción del modelo. El testing dejó de ser una etapa teórica y pasó a ser la garantía de calidad de nuestra solución de datos."

## 8.4. Cómo mostrar el repositorio

Si piden ver el código, el recorrido corto es:

1. `README.md` — resultados y cómo ejecutar.
2. `src/negocio.py` — función `validar_dias_prestamo()` (BUG-01 corregido) y `eliminar_usuario()` (BUG-03 abierto).
3. `src/modelo.py` — el `Pipeline` con `SimpleImputer` y `OneHotEncoder` (BUG-04 corregido).
4. `tests/test_negocio.py` — el caso CF-06 marcado como `expectedFailure`.
5. La suite de tests corriendo: `python -m unittest discover -s tests -t .` (o la pestaña **Actions** de GitHub si el workflow está habilitado).

## 8.5. Frases para no decir

| En vez de… | Decir… |
|---|---|
| "No llegamos a arreglar ese bug." | "BUG-03 quedó priorizado como media porque existe solución de contorno; está documentado y asignado." |
| "El modelo predice bien." | "El modelo tiene 0,78 de accuracy y 0,65 de recall; preferimos ese recall antes que una precisión más alta por el costo de los falsos negativos." |
| "Los datos son inventados." | "El dataset es sintético y reproducible porque el histórico real tiene datos personales de alumnos; se genera con semilla fija y replica el comportamiento relevado." |
| "Probamos todo." | "Probamos lo que está dentro del alcance definido; carga, estrés y seguridad quedaron fuera y el riesgo está asumido y documentado." |
