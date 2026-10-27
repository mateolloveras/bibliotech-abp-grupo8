import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src import config, negocio

FECHA_FIN = pd.Timestamp(date(2026, 10, 27))
FECHA_INICIO = FECHA_FIN - pd.Timedelta(days=364)
CANTIDAD_PRESTAMOS = 900
CANTIDAD_EJEMPLARES = 205
CLAVE_DE_PRUEBA = "Biblio2026*"

CATEGORIAS = [
    "Informática",
    "Ciencias Sociales",
    "Matemática",
    "Literatura",
    "Administración",
    "Idiomas",
    "Ciencias Naturales",
    "General",
]
PESOS_CATEGORIAS = [0.26, 0.20, 0.12, 0.11, 0.10, 0.08, 0.08, 0.05]

SEDES = ["Cosquín", "Córdoba Capital", "Villa María", "Río Tercero"]
PESOS_SEDES = [0.40, 0.26, 0.20, 0.14]

PARAMETROS = {
    "intercepto": -1.90,
    "coeficiente_demoras": 0.82,
    "efecto_categoria": {
        "Informática": 0.82,
        "Ciencias Sociales": 0.54,
        "Matemática": 0.18,
        "Literatura": -0.27,
        "Administración": -0.09,
        "Idiomas": -0.54,
        "Ciencias Naturales": -0.36,
        "General": 0.00,
    },
    "efecto_tipo_usuario": {"Alumno": 0.45, "Docente": -0.99},
    "efecto_sede": {
        "Cosquín": 0.63,
        "Córdoba Capital": 0.09,
        "Villa María": -0.27,
        "Río Tercero": -0.54,
    },
    "forma_demora": 1.45,
    "escala_demora": 2.35,
    "proporcion_sin_devolver": 0.10,
}

NOMBRES = [
    "Lucía", "Mateo", "Valentina", "Santiago", "Camila", "Tomás", "Martina", "Benjamín",
    "Julieta", "Joaquín", "Agustina", "Facundo", "Micaela", "Nicolás", "Rocío", "Gonzalo",
    "Florencia", "Emiliano", "Carolina", "Federico", "Daniela", "Ignacio", "Brenda", "Lautaro",
    "Melina", "Franco", "Antonella", "Ramiro", "Sofía", "Gastón", "Abril", "Marcos",
    "Paula", "Alejo", "Victoria", "Bruno", "Celeste", "Matías", "Noelia", "Leandro",
]
APELLIDOS = [
    "Gómez", "Fernández", "Ramírez", "Sosa", "Molina", "Peralta", "Ferreyra", "Luna",
    "Bustos", "Ávila", "Ocampo", "Juárez", "Maldonado", "Cabrera", "Nieto", "Olmos",
    "Barrera", "Zárate", "Villagra", "Carrizo", "Heredia", "Moyano", "Agüero", "Brizuela",
    "Ledesma", "Paz", "Rivero", "Suárez", "Toledo", "Vega",
]

INTEGRANTES = [
    ("Mateo Lloveras", "Estudiante"),
    ("Gino Lencina", "Bibliotecario"),
    ("Santino Vidal Gallea", "Estudiante"),
    ("Christian Quispe", "Docente"),
    ("Pablo Francisco Elias", "Estudiante"),
]

TITULOS = {
    "Informática": [
        "Introducción a la Programación en Python",
        "Estructuras de Datos y Algoritmos",
        "Bases de Datos Relacionales",
        "Fundamentos de Redes de Computadoras",
        "Aprendizaje Automático Aplicado",
        "Testeo de Software: Teoría y Práctica",
        "Arquitectura de Computadoras",
        "Ingeniería de Software",
        "Ciencia de Datos con Pandas",
        "Sistemas Operativos Modernos",
    ],
    "Ciencias Sociales": [
        "Historia Argentina Contemporánea",
        "Introducción a la Sociología",
        "Metodología de la Investigación Social",
        "Psicología del Aprendizaje",
        "Antropología Cultural",
        "Educación y Sociedad",
        "Comunicación y Cultura",
        "Filosofía Política",
    ],
    "Matemática": [
        "Álgebra Lineal",
        "Análisis Matemático I",
        "Probabilidad y Estadística",
        "Matemática Discreta",
        "Cálculo Numérico",
    ],
    "Literatura": [
        "Cuentos Completos de Cortázar",
        "El Aleph",
        "Literatura Latinoamericana del Siglo XX",
        "Poesía Argentina Reunida",
        "Taller de Escritura Creativa",
    ],
    "Administración": [
        "Administración de Organizaciones",
        "Contabilidad Básica",
        "Gestión de Proyectos",
        "Marketing Digital",
        "Economía para no Economistas",
    ],
    "Idiomas": [
        "English for Information Technology",
        "Gramática Inglesa Avanzada",
        "Portugués Básico",
        "Inglés Técnico para Ingeniería",
    ],
    "Ciencias Naturales": [
        "Biología General",
        "Química Orgánica",
        "Física I",
        "Ecología y Ambiente",
    ],
    "General": [
        "Manual de Estudio Universitario",
        "Técnicas de Redacción Académica",
        "Diccionario Enciclopédico Ilustrado",
    ],
}

AUTORES = [
    "A. Gutiérrez", "M. Pereyra", "J. Domínguez", "L. Arismendi", "R. Castellanos",
    "S. Villalba", "N. Figueroa", "P. Arrieta", "C. Benítez", "E. Salvatierra",
    "D. Roldán", "V. Quiroga", "H. Mansilla", "T. Arellano", "G. Bonetto",
]


def sin_acentos(texto):
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(letra for letra in normalizado if not unicodedata.combining(letra))


def correo_de(nombre, usados):
    partes = sin_acentos(nombre.lower()).split()
    base = f"{partes[0]}.{partes[-1]}"
    correo = f"{base}@ispc.edu.ar"
    repeticion = 2
    while correo in usados:
        correo = f"{base}{repeticion}@ispc.edu.ar"
        repeticion += 1
    usados.add(correo)
    return correo


def generar_usuarios(azar):
    filas = []
    usados = set()
    nombres_generados = []
    for nombre, rol in INTEGRANTES:
        nombres_generados.append((nombre, rol))
    while len(nombres_generados) < 103:
        nombre = f"{azar.choice(NOMBRES)} {azar.choice(APELLIDOS)}"
        rol = "Docente" if azar.random() < 0.18 else "Estudiante"
        nombres_generados.append((nombre, rol))

    orden = azar.permutation(len(nombres_generados))
    nombres_generados = [nombres_generados[posicion] for posicion in orden]
    for posicion, (nombre, rol) in enumerate(nombres_generados, start=1):
        filas.append(
            {
                "ID_Usuario": f"U-{posicion:03d}",
                "Nombre": nombre,
                "Email": correo_de(nombre, usados),
                "Rol": rol,
                "Tipo_Usuario": "Docente" if rol == "Docente" else "Alumno",
                "Sede": azar.choice(SEDES, p=PESOS_SEDES),
                "Estado": config.ESTADO_ACTIVO,
                "Hash_Clave": negocio.encriptar_clave(CLAVE_DE_PRUEBA),
            }
        )
    usuarios = pd.DataFrame(filas)

    usuarios.loc[usuarios["ID_Usuario"] == "U-012", ["Nombre", "Rol", "Tipo_Usuario", "Estado"]] = [
        "Camila Ferreyra",
        "Estudiante",
        "Alumno",
        config.ESTADO_SUSPENDIDO,
    ]
    usuarios.loc[usuarios["ID_Usuario"] == "U-089", ["Nombre", "Rol", "Tipo_Usuario", "Estado"]] = [
        "Joaquín Carrizo",
        "Estudiante",
        "Alumno",
        config.ESTADO_ACTIVO,
    ]
    usuarios.loc[usuarios["ID_Usuario"] == "U-012", "Email"] = "camila.ferreyra@ispc.edu.ar"
    usuarios.loc[usuarios["ID_Usuario"] == "U-089", "Email"] = "joaquin.carrizo@ispc.edu.ar"

    fila_gino = usuarios[usuarios["Nombre"] == "Gino Lencina"].index[0]
    usuarios.loc[fila_gino, "Email"] = "gino.lencina@ispc.edu.ar"
    usuarios.loc[fila_gino, "Rol"] = "Bibliotecario"
    usuarios.loc[fila_gino, "Estado"] = config.ESTADO_ACTIVO
    for sancionado in ["U-027", "U-055", "U-071"]:
        usuarios.loc[usuarios["ID_Usuario"] == sancionado, "Estado"] = config.ESTADO_SUSPENDIDO
    return usuarios


def generar_catalogo(azar):
    filas = []
    numero = 0
    while numero < CANTIDAD_EJEMPLARES:
        for categoria in CATEGORIAS:
            for titulo in TITULOS[categoria]:
                numero += 1
                if numero > CANTIDAD_EJEMPLARES:
                    break
                edicion = (numero - 1) // 60 + 1
                nombre = titulo if edicion == 1 else f"{titulo} - Tomo {edicion}"
                anio = int(azar.integers(2008, 2025))
                mes = int(azar.integers(1, 13))
                dia = int(azar.integers(1, 29))
                filas.append(
                    {
                        "ID_Ejemplar": f"L-{numero:03d}",
                        "Titulo": nombre,
                        "Autor": azar.choice(AUTORES),
                        "ISBN": f"978-{azar.integers(100, 999)}-{azar.integers(1000, 9999)}-{numero % 10}",
                        "Categoria_Libro": categoria,
                        "Sede": azar.choice(SEDES, p=PESOS_SEDES),
                        "Stock": int(azar.integers(1, 6)),
                        "Fecha_Publicacion": pd.Timestamp(year=anio, month=mes, day=dia).strftime(
                            config.FORMATO_FECHA
                        ),
                    }
                )
            if numero >= CANTIDAD_EJEMPLARES:
                break
    catalogo = pd.DataFrame(filas)
    catalogo.loc[catalogo["ID_Ejemplar"] == "L-205", "Stock"] = 0
    return catalogo


def probabilidad_de_mora(parametros, categoria, tipo_usuario, sede, demoras_previas):
    puntaje = (
        parametros["intercepto"]
        + parametros["efecto_categoria"][categoria]
        + parametros["efecto_tipo_usuario"][tipo_usuario]
        + parametros["efecto_sede"][sede]
        + parametros["coeficiente_demoras"] * demoras_previas
    )
    return 1 / (1 + np.exp(-puntaje))


def generar_prestamos(azar, usuarios, catalogo, parametros):
    por_categoria = {
        categoria: catalogo[catalogo["Categoria_Libro"] == categoria]["ID_Ejemplar"].tolist()
        for categoria in CATEGORIAS
    }
    alumnos = usuarios[usuarios["Tipo_Usuario"] == "Alumno"]["ID_Usuario"].tolist()
    docentes = usuarios[usuarios["Tipo_Usuario"] == "Docente"]["ID_Usuario"].tolist()
    datos_usuario = usuarios.set_index("ID_Usuario")

    dias_corridos = (FECHA_FIN - FECHA_INICIO).days
    fechas = sorted(
        FECHA_INICIO + pd.Timedelta(days=int(azar.integers(0, dias_corridos)))
        for _ in range(CANTIDAD_PRESTAMOS)
    )

    historial = {identificador: 0 for identificador in usuarios["ID_Usuario"]}
    filas = []
    for numero, fecha_prestamo in enumerate(fechas, start=1):
        es_alumno = azar.random() < 0.80
        id_usuario = azar.choice(alumnos if es_alumno else docentes)
        tipo_usuario = datos_usuario.loc[id_usuario, "Tipo_Usuario"]
        sede = datos_usuario.loc[id_usuario, "Sede"]
        categoria = azar.choice(CATEGORIAS, p=PESOS_CATEGORIAS)
        id_ejemplar = azar.choice(por_categoria[categoria])
        dias_pactados = int(azar.choice([3, 5, 7, 10, 14], p=[0.10, 0.15, 0.40, 0.15, 0.20]))
        fecha_pactada = fecha_prestamo + pd.Timedelta(days=dias_pactados)
        demoras_previas = historial[id_usuario]

        probabilidad = probabilidad_de_mora(parametros, categoria, tipo_usuario, sede, demoras_previas)
        es_tardia = azar.random() < probabilidad

        if fecha_pactada > FECHA_FIN:
            fecha_real = pd.NaT
        elif es_tardia and azar.random() < parametros["proporcion_sin_devolver"]:
            fecha_real = pd.NaT
        elif es_tardia:
            retraso = int(np.ceil(azar.gamma(parametros["forma_demora"], parametros["escala_demora"])))
            retraso = max(1, min(retraso, 30))
            fecha_real = fecha_pactada + pd.Timedelta(days=retraso)
            historial[id_usuario] += 1
        else:
            adelanto = int(azar.integers(0, max(2, dias_pactados)))
            fecha_real = fecha_pactada - pd.Timedelta(days=adelanto)

        filas.append(
            {
                "ID_Prestamo": f"P-{numero:03d}",
                "ID_Usuario": id_usuario,
                "ID_Ejemplar": id_ejemplar,
                "Tipo_Usuario": tipo_usuario,
                "Categoria_Libro": categoria,
                "Sede": sede,
                "Fecha_Prestamo": fecha_prestamo,
                "Fecha_Devolucion_Pactada": fecha_pactada,
                "Fecha_Devolucion_Real": fecha_real,
                "Demoras_Previas": demoras_previas,
            }
        )

    prestamos = pd.DataFrame(filas)
    prestamos = marcar_extraviados(prestamos, azar)
    prestamos = forzar_casos_de_prueba(prestamos, usuarios, catalogo)
    return prestamos


def marcar_extraviados(prestamos, azar, cantidad=9):
    tardios = prestamos[
        prestamos["Fecha_Devolucion_Real"].notna()
        & (prestamos["Fecha_Devolucion_Real"] > prestamos["Fecha_Devolucion_Pactada"])
    ]
    elegidos = azar.choice(tardios.index.to_numpy(), size=cantidad, replace=False)
    for indice in elegidos:
        dias = int(azar.integers(95, 210))
        prestamos.loc[indice, "Fecha_Devolucion_Real"] = prestamos.loc[
            indice, "Fecha_Devolucion_Pactada"
        ] + pd.Timedelta(days=dias)
    return prestamos


def contar_demoras(prestamos, id_usuario):
    propios = prestamos[prestamos["ID_Usuario"] == id_usuario].dropna(subset=["Fecha_Devolucion_Real"])
    if propios.empty:
        return 0
    demora = (propios["Fecha_Devolucion_Real"] - propios["Fecha_Devolucion_Pactada"]).dt.days
    return int((demora > 0).sum())


def forzar_casos_de_prueba(prestamos, usuarios, catalogo):
    nuevos = []
    base = len(prestamos)
    pendientes = [
        ("U-089", "L-014", 7, 1),
        ("U-089", "L-103", 14, 5),
        ("U-012", "L-032", 7, 2),
        ("U-005", "L-007", 7, 0),
    ]
    for posicion, (id_usuario, id_ejemplar, dias, faltan) in enumerate(pendientes, start=1):
        datos_usuario = usuarios[usuarios["ID_Usuario"] == id_usuario].iloc[0]
        datos_libro = catalogo[catalogo["ID_Ejemplar"] == id_ejemplar].iloc[0]
        fecha_pactada = FECHA_FIN + pd.Timedelta(days=faltan)
        nuevos.append(
            {
                "ID_Prestamo": f"P-{base + posicion:03d}",
                "ID_Usuario": id_usuario,
                "ID_Ejemplar": id_ejemplar,
                "Tipo_Usuario": datos_usuario["Tipo_Usuario"],
                "Categoria_Libro": datos_libro["Categoria_Libro"],
                "Sede": datos_usuario["Sede"],
                "Fecha_Prestamo": fecha_pactada - pd.Timedelta(days=dias),
                "Fecha_Devolucion_Pactada": fecha_pactada,
                "Fecha_Devolucion_Real": pd.NaT,
                "Demoras_Previas": contar_demoras(prestamos, id_usuario),
            }
        )
    return pd.concat([prestamos, pd.DataFrame(nuevos)], ignore_index=True)


def formatear_fechas(prestamos):
    salida = prestamos.copy()
    for columna in ["Fecha_Prestamo", "Fecha_Devolucion_Pactada", "Fecha_Devolucion_Real"]:
        salida[columna] = pd.to_datetime(salida[columna]).dt.strftime(config.FORMATO_FECHA)
    return salida


def generar(parametros=None, semilla=None):
    parametros = parametros or PARAMETROS
    azar = np.random.default_rng(semilla or config.SEMILLA)
    usuarios = generar_usuarios(azar)
    catalogo = generar_catalogo(azar)
    prestamos = generar_prestamos(azar, usuarios, catalogo, parametros)
    return prestamos, usuarios, catalogo


def main():
    prestamos, usuarios, catalogo = generar()
    config.CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    formatear_fechas(prestamos).to_csv(config.ARCHIVO_PRESTAMOS, index=False, encoding="utf-8")
    usuarios.to_csv(config.ARCHIVO_USUARIOS, index=False, encoding="utf-8")
    catalogo.to_csv(config.ARCHIVO_CATALOGO, index=False, encoding="utf-8")
    print(f"Préstamos generados: {len(prestamos)} -> {config.ARCHIVO_PRESTAMOS}")
    print(f"Usuarios generados: {len(usuarios)} -> {config.ARCHIVO_USUARIOS}")
    print(f"Ejemplares generados: {len(catalogo)} -> {config.ARCHIVO_CATALOGO}")


if __name__ == "__main__":
    main()
