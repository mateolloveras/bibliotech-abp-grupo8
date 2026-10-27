# 9. Preguntas posibles de la defensa (y cómo las respondemos)

Preparamos las respuestas que nos parecieron más probables, agrupadas por materia. Todas se pueden verificar en el repositorio.

## 9.1. Testeo de Software

**¿Cuál es la diferencia entre error, defecto y fallo?**
Un **error** es la equivocación humana (escribir `<` en lugar de `<=`). Ese error deja un **defecto** en el código (la condición `dias < 16`). Cuando el código se ejecuta con el dato adecuado, el defecto produce un **fallo** observable: el sistema acepta una reserva de 15 días. Es exactamente el recorrido del BUG-01.

**¿Qué diferencia hay entre verificación y validación?**
Verificar es comprobar que construimos el producto **de acuerdo a la especificación** (el plazo máximo es de 14 días y el sistema lo respeta). Validar es comprobar que el producto **sirve para lo que el usuario necesita** (que el bibliotecario pueda registrar un préstamo sin tocar código, que es lo que miden las pruebas de usabilidad).

**¿Qué técnicas de caja negra usaron y por qué?**
Partición en clases de equivalencia (dividimos las entradas en grupos que el sistema trata igual: días válidos, días inválidos; usuario activo, usuario suspendido) y análisis de valores límite (los errores se esconden en los bordes: 0, 1, 14, 15). También aplicamos no enmascaramiento de errores: cada dato inválido se prueba por separado para que un error no tape al siguiente.

**¿Por qué dejaron fuera las pruebas de carga y de seguridad?**
Por el tipo de producto en esta etapa: el MVP corre en una instancia de máquina virtual por sesión de usuario, así que no hay concurrencia real para medir, y no hay datos sensibles expuestos en un servidor. Es una decisión de alcance con el riesgo asumido y documentado, no un olvido. Cuando el sistema se despliegue como web, ambas entran al alcance.

**¿Cuál es la diferencia entre severidad y prioridad? Den un ejemplo del proyecto.**
La severidad mide el impacto técnico; la prioridad, la urgencia del negocio. BUG-03 tiene severidad **crítica** (rompe la integridad referencial: quedan préstamos huérfanos) pero prioridad **media**, porque el bibliotecario puede suspender al usuario en lugar de eliminarlo. Al revés, BUG-02 tiene severidad media (nada se rompe) pero prioridad alta, porque el correo le llega al alumno sin fecha y pierde sentido.

**¿Por qué hay un test que falla a propósito?**
Porque CF-06 documenta un defecto abierto. Si lo borráramos, la suite daría 100 % en verde y el defecto quedaría escondido en un informe. Marcándolo como `expectedFailure`, cada corrida deja constancia de que BUG-03 sigue sin resolverse, y el día que se corrija el test va a avisar que ya pasa.

**¿Cómo saben que una corrección no rompió otra cosa?**
Después de cada corrección corremos la suite completa (pruebas de confirmación más regresión). Son 36 tests automatizados que cubren los casos CF, BT y PI, y además corren solos en GitHub Actions en cada push.

**¿Qué es el criterio de salida y lo cumplieron?**
Es la condición que define cuándo se puede cerrar la etapa de pruebas: 100 % de casos ejecutados, al menos 85 % exitosos y 100 % de los defectos bloqueantes corregidos. Lo cumplimos: 24 de 24 ejecutados, 95,8 % exitosos tras el re-testing y los dos defectos urgentes (BUG-01 y BUG-04) cerrados y verificados.

**¿Qué pruebas de integración hicieron, exactamente?**
Cuatro: catálogo con la interfaz (PI-01), reserva sincronizando préstamos y stock (PI-02), datos con el pipeline del modelo y la interfaz de alertas (PI-03) y score del modelo con el módulo de notificaciones (PI-04). PI-03 es la que encontró el BUG-04, que no aparecía probando el modelo por separado.

## 9.2. Práctica Profesionalizante

**¿Por qué eligieron regresión logística y no otro modelo?**
Porque el problema es de clasificación binaria (se demora o no), porque es interpretable —podemos mostrar el peso de cada variable y explicarle al bibliotecario por qué un préstamo es riesgoso— y porque es un **modelo base**: necesitábamos un punto de comparación antes de probar algo más complejo. Para la entrega final lo vamos a comparar contra un árbol de decisión.

**¿Qué hicieron con los valores nulos?**
Los nulos están solo en `Fecha_Devolucion_Real` y corresponden a préstamos vigentes. Los excluimos del cálculo del promedio de demora y del entrenamiento en lugar de imputarlos, porque imputar una fecha inventada distorsionaría la métrica y le enseñaría al modelo un resultado que todavía no ocurrió. Distinto es el caso de la categoría vacía en la inferencia: ahí sí imputamos "General", porque necesitamos devolver una predicción sin cortar la ejecución.

**¿Y con los outliers?**
Detectamos 9 préstamos con más de 90 días de demora. No los borramos: los documentamos aparte como ejemplares reportados perdidos, porque no son demoras de devolución sino bajas de ejemplares. Si los dejáramos dentro, el promedio pasaría de 4 días a más de 5 y sería un número que no describe a ningún caso real.

**Las métricas no son altas, ¿no es un problema?**
Para un modelo base entrenado con 839 registros y cuatro variables, 0,78 de accuracy es un punto de partida razonable. Lo importante es cómo se usa: no bloquea ninguna operación, solo prioriza recordatorios. Un falso positivo cuesta un correo de más; un falso negativo cuesta un libro que no vuelve. Por eso el objetivo de la próxima iteración es subir el recall de 0,65, aunque baje algo la precisión.

**¿Por qué usan accuracy si las clases están desbalanceadas?**
Están desbalanceadas pero no de forma extrema: 35,3 % de devoluciones tardías. Igual no miramos solo accuracy, por eso reportamos precisión, recall y la matriz de confusión, que es la que muestra los 26 falsos negativos.

**¿El modelo decide si se presta el libro?**
No. Las reglas de negocio corren primero y son las que pueden rechazar la reserva (mora activa, falta de stock, plazo fuera de rango). El modelo se ejecuta después y solo clasifica el riesgo para priorizar el recordatorio. Es una decisión de diseño: no queremos que un modelo estadístico le niegue un libro a un alumno.

**¿Los datos son reales?**
El dataset publicado es sintético y reproducible. Lo generamos con [`scripts/generar_datos.py`](../scripts/generar_datos.py) con una semilla fija, replicando el comportamiento relevado del histórico (categorías más pedidas, distribución de plazos, tasa de mora por sede). Lo hicimos así porque el histórico real tiene nombres y correos de alumnos y no podemos publicarlos en un repositorio abierto. Cualquiera que clone el repositorio obtiene exactamente los mismos números del informe.

**¿Qué pasa si se reinicia Colab?**
Se pierden los usuarios y préstamos cargados en la sesión, porque trabajamos con DataFrames en memoria. Está listado como limitación conocida, y la solución prevista es exportar los movimientos a CSV o pasar a SQLite.

## 9.3. Sobre el proyecto y el trabajo en equipo

**¿Qué cambió respecto de la Evidencia 1?**
El alcance funcional se mantiene. Lo que cambió es la capa de presentación: en lugar de desplegar una aplicación web con servidor, centralizamos el MVP en un notebook interactivo, lo que nos permitió llegar al flujo completo de punta a punta dentro del plazo. El cambio está justificado en la [documentación técnica](07_arquitectura_y_stack.md).

**¿Cómo se repartieron el trabajo?**
Gino coordinó el plan de pruebas y el reporte de bugs; Mateo y Santino diseñaron y ejecutaron los casos funcionales; Christian y Pablo se ocuparon de las pruebas de integración y usabilidad y del ajuste del modelo. El detalle está en los [recursos del plan de pruebas](03_plan_de_pruebas.md) y en la [bitácora](11_bitacora_del_grupo.md).

**Si tuvieran una semana más, ¿qué harían?**
Tres cosas, en este orden: resolver el BUG-03 con baja lógica, agregar la variable de renovaciones y comparar la regresión logística contra un árbol de decisión, y hacer que los movimientos de la sesión persistan en disco.

**¿Qué aprendieron?**
Que el testing no es una etapa al final. Los casos de valores límite encontraron un error que el código "funcionando" no mostraba, y las pruebas de integración encontraron un error que ninguna de las dos partes mostraba por separado. Escribir los casos antes de probar nos obligó a entender mejor las reglas del negocio.
