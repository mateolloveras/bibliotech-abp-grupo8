# 10. Anexo — E-Commerce Insight (trabajo previo de Práctica Profesionalizante)

> **Nota del grupo:** este documento corresponde a una **actividad anterior** de Práctica Profesionalizante I, previa a la definición de BiblioTech. Lo dejamos en el repositorio porque de ahí salieron la estructura de requerimientos (RF1 a RF5) y la forma de encarar el análisis exploratorio que después reutilizamos en BiblioTech. **No forma parte del alcance de la Evidencia 3**: el proyecto que se defiende es BiblioTech.

## E-Commerce Insight: Sistema de Análisis de Ventas

**Integrantes del grupo:** Pablo Francisco Elias · Christian Quispe · Santino Vidal · Gino Agustin Lencina · Mateo Lloveras

### Descripción de las actividades a las que el producto da soporte

El producto desarrollado da soporte al análisis de la información generada por las ventas de una empresa de comercio electrónico. Permite explorar y analizar datos relacionados con los pedidos realizados, las categorías de productos, las regiones donde se producen las ventas, los precios, descuentos, métodos de pago, tiempos de entrega, calificaciones de los clientes e ingresos obtenidos.

Además, facilita la identificación de patrones y tendencias a partir de los datos, permitiendo obtener información útil para apoyar la toma de decisiones. Mediante el análisis exploratorio y las visualizaciones generadas, se pueden conocer aspectos relevantes del funcionamiento comercial y detectar oportunidades de mejora.

### Pain points identificados

- **Dificultad para analizar grandes volúmenes de información:** los datos de ventas contienen múltiples variables, lo que dificulta obtener conclusiones rápidamente mediante una revisión manual.
- **Falta de información visual para la toma de decisiones:** sin gráficos o visualizaciones, resulta más complejo identificar tendencias, distribuciones y relaciones entre las diferentes variables.
- **Dificultad para detectar problemas en los datos:** pueden existir valores nulos, registros duplicados o inconsistencias que afectan la calidad y confiabilidad del análisis.
- **Falta de conocimiento sobre el comportamiento de las ventas:** resulta necesario identificar qué categorías, regiones, métodos de pago y otras variables presentan determinados comportamientos.
- **Necesidad de analizar indicadores comerciales:** la organización necesita conocer información relacionada con los ingresos, descuentos aplicados, cantidades vendidas, tiempos de entrega y satisfacción de los clientes.

### Relevamiento de requerimientos funcionales

**RF1. Carga y procesamiento de datos.** El sistema deberá permitir cargar y procesar el conjunto de datos de ventas para realizar su posterior análisis.

**RF2. Análisis de calidad de datos.** El sistema deberá identificar valores nulos, registros duplicados y posibles inconsistencias presentes en el conjunto de datos.

**RF3. Generación de estadísticas descriptivas.** El sistema deberá generar estadísticas descriptivas de las variables numéricas y categóricas, permitiendo conocer frecuencias, promedios, medianas y otros indicadores relevantes.

**RF4. Generación de visualizaciones.** El sistema deberá generar gráficos que permitan visualizar la distribución de las variables numéricas y categóricas.

**RF5. Análisis de relaciones entre variables.** El sistema deberá permitir analizar la relación entre diferentes variables, como ingresos, categorías de productos, regiones, precios, descuentos y otros indicadores.

### Relevamiento de requerimientos no funcionales

**RNF1. Usabilidad.** El producto deberá presentar los resultados de manera clara y comprensible, facilitando la interpretación de la información obtenida.

**RNF2. Rendimiento.** El sistema deberá procesar el conjunto de datos y generar los resultados en un tiempo razonable.

**RNF3. Confiabilidad.** El sistema deberá realizar los cálculos y análisis de forma correcta, proporcionando resultados consistentes y confiables.

**RNF4. Mantenibilidad.** El código deberá estar organizado y documentado para facilitar futuras modificaciones, mejoras o incorporación de nuevas funcionalidades.

**RNF5. Compatibilidad.** El sistema deberá poder ejecutarse en un entorno con Python y las bibliotecas necesarias para el análisis y visualización de datos.

---

## Qué de todo esto sobrevive en BiblioTech

| De E-Commerce Insight | Cómo quedó en BiblioTech |
|---|---|
| RF1 (carga y procesamiento) | [`src/datos.py`](../src/datos.py) — `cargar_prestamos()`, `cargar_usuarios()`, `cargar_catalogo()` |
| RF2 (calidad de datos) | `controlar_calidad()` e `informe_de_calidad()`, más la separación de préstamos vigentes y extraviados |
| RF3 (estadísticas descriptivas) | [`src/eda.py`](../src/eda.py) — `estadisticas_numericas()`, `estadisticas_categoricas()` |
| RF4 (visualizaciones) | Los tres gráficos del EDA en [`docs/evidencias/`](evidencias) |
| RF5 (relaciones entre variables) | `tasa_de_mora_por_sede()` y los coeficientes del modelo (`importancia_de_variables()`) |
| RNF1 a RNF5 | Se mantuvieron tal cual, adaptando los ejemplos al dominio de biblioteca ([requerimientos](02_requerimientos.md)) |

El salto entre un trabajo y el otro es que BiblioTech **no se queda en el análisis**: además de describir lo que pasó, predice el riesgo de cada préstamo nuevo y lo integra a una interfaz que el bibliotecario puede usar.
