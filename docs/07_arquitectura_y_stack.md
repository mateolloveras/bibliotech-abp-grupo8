# 7. Documentación técnica: arquitectura y stack

## 7.1. Arquitectura del MVP

El prototipo está organizado en cuatro capas. La interfaz nunca toca los datos directamente: siempre pasa por la capa de reglas de negocio, y el modelo se consume a través de un único punto de entrada.

```
┌─────────────────────────────────────────────────────────────┐
│  INTERFAZ (src/interfaz.py + notebooks/BiblioTech_MVP.ipynb)│
│  Login · Catálogo · Reservas · Usuarios · Riesgo · Dashboard│
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                v                             v
┌─────────────────────────────┐   ┌───────────────────────────┐
│  REGLAS DE NEGOCIO          │   │  MODELO PREDICTIVO        │
│  src/negocio.py             │──>│  src/modelo.py            │
│  Días 1-14 · mora · stock   │   │  Pipeline + LogisticReg.  │
│  altas · notificaciones     │<──│  predecir_riesgo()        │
└───────────────┬─────────────┘   └─────────────┬─────────────┘
                │                               │
                v                               v
┌─────────────────────────────────────────────────────────────┐
│  DATOS Y ANÁLISIS (src/datos.py · src/eda.py)               │
│  Carga · control de calidad · estadísticas · gráficos       │
└───────────────────────────┬─────────────────────────────────┘
                            v
┌─────────────────────────────────────────────────────────────┐
│  PERSISTENCIA (data/*.csv)                                  │
│  prestamos_historicos.csv · usuarios.csv · catalogo.csv     │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de punta a punta de una reserva

```
Usuario elige libro y días en el formulario
        │
        v
negocio.registrar_reserva()
        ├── obtener_usuario()        ¿existe?
        ├── esta_sancionado()        ¿tiene mora activa?      -> 🚫 corta acá
        ├── hay_stock()              ¿queda ejemplar?          -> ❌ corta acá
        ├── validar_dias_prestamo()  ¿está entre 1 y 14?      -> ❌ corta acá
        ├── calcular_fecha_devolucion()
        ├── agrega la fila a df_prestamos
        └── descuenta 1 en df_catalogo
        │
        v
modelo.predecir_riesgo()  ->  probabilidad + nivel (BAJO / MEDIO / ALTO)
        │
        v
negocio.generar_notificacion_vencimiento()  (solo si el riesgo es ALTO)
        │
        v
La interfaz muestra la confirmación, el semáforo de riesgo y el aviso
```

El orden de las validaciones no es casual: primero las reglas duras del negocio y recién después la predicción. El modelo **no decide** si se presta o no un libro; solo prioriza a quién conviene recordarle la devolución.

## 7.2. Stack tecnológico y justificación de los cambios

| Capa | Tecnología implementada | Justificación y cambios respecto de la Evidencia 1 |
|---|---|---|
| Entorno de ejecución e interfaz | Google Colaboratory + ipywidgets | **Cambio justificado:** en la Evidencia 1 habíamos planteado una aplicación web con servidor. Para esta fase Beta centralizamos el MVP en un notebook interactivo, que cumple RNF5 (compatibilidad) y RNF1 (usabilidad) y permite que los docentes ejecuten todo el flujo desde el navegador con un clic, sin instalar nada. |
| Lenguaje y procesamiento de datos | Python 3 + Pandas + NumPy | Soporte para la carga del dataset (RF1), detección de nulos y duplicados (RF2) y cálculo de estadísticas descriptivas (RF3). |
| Visualización | Matplotlib + Seaborn | Gráficos de distribución de préstamos, ranking de categorías y mora por sede (RF4 y RF5), renderizados en el dashboard. |
| Machine Learning | Scikit-Learn (`Pipeline`, `ColumnTransformer`, `SimpleImputer`, `OneHotEncoder`, `StandardScaler`, `LogisticRegression`) | Encapsula el preprocesamiento junto con el clasificador, lo que garantiza RNF3 (confiabilidad) y evita el error del BUG-04. |
| Persistencia | Archivos CSV versionados en el repositorio | **Cambio justificado:** descartamos una base de datos relacional en esta etapa porque agregaba infraestructura sin aportar al objetivo del MVP. Es una limitación conocida: los datos cargados durante la sesión no persisten. |
| Pruebas | `unittest` (librería estándar) | Permite correr la suite tanto en Colab como en local sin instalar dependencias extra. |
| Control de versiones e integración continua | Git + GitHub (workflow de GitHub Actions incluido) | Trazabilidad del código (RNF4) y ejecución de los 36 tests, en local con un comando y en GitHub Actions cuando el workflow está habilitado. |

## 7.3. Estructura del repositorio

```
.
├── data/                        Datasets del proyecto
│   ├── prestamos_historicos.csv Histórico de 904 préstamos (12 meses)
│   ├── usuarios.csv             Padrón de 103 usuarios
│   └── catalogo.csv             205 ejemplares
├── docs/                        Documentación de las dos materias
│   ├── 01_alcance_y_objetivos.md
│   ├── 02_requerimientos.md
│   ├── 03_plan_de_pruebas.md
│   ├── 04_casos_de_prueba.md
│   ├── 05_reporte_de_defectos.md
│   ├── 06_eda_y_modelo.md
│   ├── 07_arquitectura_y_stack.md
│   ├── 08_guion_de_defensa.md
│   ├── 09_preguntas_de_defensa.md
│   ├── 10_anexo_ecommerce_insight.md
│   ├── 11_bitacora_del_grupo.md
│   └── evidencias/              Gráficos y salidas de ejecución
├── notebooks/
│   └── BiblioTech_MVP.ipynb     Notebook interactivo (Google Colab)
├── scripts/
│   ├── generar_datos.py         Genera los CSV de forma reproducible
│   ├── generar_evidencias.py    Genera los gráficos del EDA
│   └── demo_flujo.py            Recorre el flujo completo por consola
├── src/
│   ├── config.py                Constantes, umbrales y mensajes
│   ├── datos.py                 Carga y control de calidad (RF1, RF2)
│   ├── eda.py                   Estadísticas y gráficos (RF3, RF4, RF5)
│   ├── negocio.py               Reglas de negocio (RF6 a RF10)
│   ├── modelo.py                Pipeline y predicción (RF11)
│   └── interfaz.py              Paneles interactivos con ipywidgets
├── tests/
│   ├── test_datos.py            Calidad de datos y conclusiones del EDA
│   ├── test_negocio.py          Casos CF-01 a CF-08 y BT-01 a BT-08
│   ├── test_modelo.py           Métricas y BT-06
│   └── test_integracion.py      Casos PI-01 a PI-04
├── requirements.txt
└── README.md
```

## 7.4. Decisiones técnicas que vale la pena explicar

1. **Todo el preprocesamiento vive dentro del `Pipeline`.** Si imputáramos y codificáramos "a mano" antes de entrenar, en producción alguien se olvidaría de repetir esos pasos y el modelo recibiría datos distintos a los del entrenamiento. Además, fue la solución del BUG-04.
2. **Los mensajes están centralizados en `config.py`.** Así el texto que valida el test es exactamente el mismo que ve el usuario, y cambiar un mensaje no obliga a tocar los tests uno por uno.
3. **Las funciones de negocio no imprimen.** Devuelven un diccionario con `ok` y `mensaje`, y la interfaz decide cómo mostrarlo. Eso permite probar las reglas sin levantar la interfaz.
4. **Las contraseñas se guardan con hash SHA-256.** Es un entorno de prueba, pero no queríamos dejar contraseñas en texto plano dentro de un CSV público.
5. **El dataset es sintético y reproducible.** `scripts/generar_datos.py` usa una semilla fija, así que cualquiera que clone el repositorio obtiene exactamente los mismos números del informe.
6. **El defecto abierto queda en el código.** `eliminar_usuario()` no valida préstamos activos a propósito: es BUG-03 y está documentado como tal. La función `tiene_prestamos_activos()` ya existe para resolverlo en la próxima iteración.

## 7.5. Requisitos de ejecución

| Requisito | Versión |
|---|---|
| Python | 3.10 o superior |
| pandas | 2.x |
| numpy | 1.26 o superior |
| scikit-learn | 1.4 o superior |
| matplotlib | 3.8 o superior |
| seaborn | 0.13 o superior |
| ipywidgets | 8.x |
