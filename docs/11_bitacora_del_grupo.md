# 11. Bitácora del grupo

Registro corto de cómo avanzamos, para tenerlo a mano en la defensa.

## Semana 1 — Planificación

- Revisamos el alcance definido en la Evidencia 1 y confirmamos que no había cambios; sumamos los criterios de aceptación que antes no se habían pedido.
- Actualizamos el alcance del testing incorporando el módulo de gestión de usuarios y eligiendo las dos pruebas optativas: **integración** y **usabilidad**.
- Repartimos responsabilidades entre los cinco integrantes.
- Diseñamos los casos CF-01 a CF-08 y revisamos los BT heredados de la Evidencia 2.

## Semana 2 — Diseño y primeras ejecuciones

- Aplicamos valores límite y clases de equivalencia sobre las reglas de negocio.
- Primera corrida de los casos funcionales: **20 de 24 OK (83,3 %)**, por debajo del criterio de salida.
- Aparecieron BUG-01 (acepta 15 días) y BUG-02 (`Fecha límite: None` en el correo).
- Decidimos centralizar los mensajes del sistema en `config.py` para que el texto que valida el test sea el mismo que ve el usuario.

## Semana 3 — Integración y corrección

- Conectamos los DataFrames, el modelo y la interfaz en el notebook.
- PI-03 destapó el **BUG-04**: un registro con la categoría vacía cortaba la celda con `ValueError`. Lo resolvimos metiendo `SimpleImputer` y `OneHotEncoder(handle_unknown="ignore")` dentro del `Pipeline`.
- Corregimos BUG-01 y BUG-02 y ejecutamos el re-testing: **23 de 24 OK (95,8 %)**.
- Discutimos qué hacer con **BUG-03**. Conclusión: severidad crítica pero prioridad media, porque existe solución de contorno. Queda asignado y marcado como `expectedFailure` en la suite.

## Semana 4 — Cierre

- Pruebas de usabilidad con los integrantes simulando el rol de bibliotecario (PU-01 a PU-04).
- Generamos las evidencias visuales y la salida de la demo.
- Documentamos arquitectura, stack y justificación de los cambios respecto de la Evidencia 1.
- Armamos el guion de la defensa y las preguntas posibles.

## Decisiones que discutimos y por qué quedaron así

| Discusión | Decisión | Motivo |
|---|---|---|
| ¿Imputamos las fechas de devolución faltantes? | No, se excluyen. | Son préstamos vigentes: inventar una fecha distorsiona el promedio de demora. |
| ¿Borramos los préstamos con más de 90 días? | No, se documentan aparte. | Son ejemplares perdidos; sacarlos sin explicarlos sería esconder información. |
| ¿Usamos base de datos o CSV? | CSV versionados. | Para el MVP agregaba infraestructura sin aportar al objetivo. Queda como limitación conocida. |
| ¿Arreglamos BUG-03 a las apuradas? | No. | Preferimos documentarlo bien y resolverlo con baja lógica, en vez de parchearlo sin pensar la integridad referencial. |
| ¿Dejamos el test de CF-06 afuera de la suite? | No, queda como fallo esperado. | Un defecto abierto tiene que verse en cada corrida. |
| ¿Publicamos el histórico real de préstamos? | No, generamos un dataset sintético reproducible. | El histórico real tiene nombres y correos de alumnos. |
