import hashlib
from datetime import datetime

import pandas as pd

from src import config


def encriptar_clave(clave):
    return hashlib.sha256(str(clave).encode("utf-8")).hexdigest()


def validar_dias_prestamo(dias):
    try:
        dias = int(dias)
    except (TypeError, ValueError):
        return {"ok": False, "mensaje": config.MENSAJES["dias_fuera_de_rango"]}
    if config.DIAS_MINIMOS_PRESTAMO <= dias <= config.DIAS_MAXIMOS_PRESTAMO:
        return {"ok": True, "mensaje": "", "dias": dias}
    return {"ok": False, "mensaje": config.MENSAJES["dias_fuera_de_rango"]}


def calcular_fecha_devolucion(fecha_prestamo, dias):
    return pd.to_datetime(fecha_prestamo) + pd.Timedelta(days=int(dias))


def obtener_usuario(df_usuarios, id_usuario):
    encontrados = df_usuarios[df_usuarios["ID_Usuario"] == id_usuario]
    if encontrados.empty:
        return None
    return encontrados.iloc[0]


def esta_sancionado(df_usuarios, id_usuario):
    usuario = obtener_usuario(df_usuarios, id_usuario)
    if usuario is None:
        return False
    return usuario["Estado"] == config.ESTADO_SUSPENDIDO


def autenticar(df_usuarios, email, clave):
    encontrados = df_usuarios[df_usuarios["Email"].str.lower() == str(email).lower()]
    if encontrados.empty:
        return {"ok": False, "mensaje": config.MENSAJES["credenciales_invalidas"]}
    usuario = encontrados.iloc[0]
    if usuario["Hash_Clave"] != encriptar_clave(clave):
        return {"ok": False, "mensaje": config.MENSAJES["credenciales_invalidas"]}
    nombre = usuario["Nombre"]
    rol = usuario["Rol"]
    return {
        "ok": True,
        "mensaje": f"Bienvenido {nombre} (Rol: {rol})",
        "sesion": {
            "activa": True,
            "ID_Usuario": usuario["ID_Usuario"],
            "Nombre": nombre,
            "Rol": rol,
        },
    }


def cerrar_sesion(sesion=None):
    return {"activa": False, "ID_Usuario": None, "Nombre": None, "Rol": None}


def siguiente_id(df, columna, prefijo):
    if df.empty:
        return f"{prefijo}-001"
    numeros = df[columna].astype(str).str.split("-").str[1].astype(int)
    return f"{prefijo}-{numeros.max() + 1:03d}"


def registrar_usuario(df_usuarios, nombre, email, rol, clave="Biblio2026*", sede="Córdoba Capital"):
    if not str(nombre).strip():
        return {"ok": False, "mensaje": config.MENSAJES["nombre_obligatorio"], "usuarios": df_usuarios}
    if not str(email).strip():
        return {"ok": False, "mensaje": config.MENSAJES["email_obligatorio"], "usuarios": df_usuarios}
    nuevo_id = siguiente_id(df_usuarios, "ID_Usuario", "U")
    nuevo = {
        "ID_Usuario": nuevo_id,
        "Nombre": str(nombre).strip(),
        "Email": str(email).strip(),
        "Rol": rol,
        "Tipo_Usuario": "Docente" if rol == "Docente" else "Alumno",
        "Sede": sede,
        "Estado": config.ESTADO_ACTIVO,
        "Hash_Clave": encriptar_clave(clave),
    }
    usuarios = pd.concat([df_usuarios, pd.DataFrame([nuevo])], ignore_index=True)
    return {
        "ok": True,
        "mensaje": config.MENSAJES["usuario_creado"],
        "ID_Usuario": nuevo_id,
        "usuarios": usuarios,
    }


def editar_usuario(df_usuarios, id_usuario, nuevos_datos):
    usuarios = df_usuarios.copy()
    filtro = usuarios["ID_Usuario"] == id_usuario
    if not filtro.any():
        return {"ok": False, "mensaje": config.MENSAJES["usuario_inexistente"], "usuarios": usuarios}
    for columna, valor in nuevos_datos.items():
        if columna == "ID_Usuario":
            continue
        usuarios.loc[filtro, columna] = valor
    return {"ok": True, "mensaje": config.MENSAJES["usuario_actualizado"], "usuarios": usuarios}


def buscar_usuario(df_usuarios, termino):
    termino = str(termino).strip()
    if not termino:
        return df_usuarios
    coincide_nombre = df_usuarios["Nombre"].str.contains(termino, case=False, na=False)
    coincide_email = df_usuarios["Email"].str.contains(termino, case=False, na=False)
    return df_usuarios[coincide_nombre | coincide_email]


def tiene_prestamos_activos(df_prestamos, id_usuario):
    propios = df_prestamos[df_prestamos["ID_Usuario"] == id_usuario]
    if propios.empty:
        return False
    return bool(propios["Fecha_Devolucion_Real"].isna().any())


def eliminar_usuario(df_usuarios, id_usuario):
    usuarios = df_usuarios.copy()
    filtro = usuarios["ID_Usuario"] == id_usuario
    if not filtro.any():
        return {"ok": False, "mensaje": config.MENSAJES["usuario_inexistente"], "usuarios": usuarios}
    usuarios = usuarios[~filtro].reset_index(drop=True)
    return {"ok": True, "mensaje": config.MENSAJES["usuario_eliminado"], "usuarios": usuarios}


def buscar_en_catalogo(df_catalogo, termino="", categoria=None):
    avisos = []
    termino = str(termino)
    if len(termino) > config.LONGITUD_MAXIMA_BUSQUEDA:
        termino = termino[: config.LONGITUD_MAXIMA_BUSQUEDA]
        avisos.append(config.MENSAJES["busqueda_muy_larga"])
    resultados = df_catalogo
    if termino.strip():
        buscado = termino.strip()
        coincide_titulo = resultados["Titulo"].str.contains(buscado, case=False, na=False, regex=False)
        coincide_autor = resultados["Autor"].str.contains(buscado, case=False, na=False, regex=False)
        coincide_isbn = resultados["ISBN"].str.contains(buscado, case=False, na=False, regex=False)
        resultados = resultados[coincide_titulo | coincide_autor | coincide_isbn]
    if categoria and categoria != "Todas":
        resultados = resultados[resultados["Categoria_Libro"] == categoria]
    return {"resultados": resultados, "avisos": avisos, "termino_usado": termino}


def obtener_ejemplar(df_catalogo, id_ejemplar):
    encontrados = df_catalogo[df_catalogo["ID_Ejemplar"] == id_ejemplar]
    if encontrados.empty:
        return None
    return encontrados.iloc[0]


def hay_stock(df_catalogo, id_ejemplar):
    ejemplar = obtener_ejemplar(df_catalogo, id_ejemplar)
    if ejemplar is None:
        return False
    return int(ejemplar["Stock"]) > 0


def validar_fecha_publicacion(texto, hoy=None):
    hoy = pd.to_datetime(hoy) if hoy is not None else pd.Timestamp.today().normalize()
    try:
        fecha = datetime.strptime(str(texto).strip(), config.FORMATO_FECHA)
    except ValueError:
        return {"ok": False, "mensaje": config.MENSAJES["fecha_invalida"]}
    if pd.Timestamp(fecha) > hoy:
        return {"ok": False, "mensaje": config.MENSAJES["fecha_futura"]}
    return {"ok": True, "mensaje": "", "fecha": pd.Timestamp(fecha)}


def dar_de_alta_ejemplar(df_catalogo, titulo, autor, isbn, categoria, sede, stock, fecha_publicacion, hoy=None):
    if not str(titulo).strip():
        return {"ok": False, "mensaje": "❌ Error: El campo Título es obligatorio", "catalogo": df_catalogo}
    validacion = validar_fecha_publicacion(fecha_publicacion, hoy=hoy)
    if not validacion["ok"]:
        return {"ok": False, "mensaje": validacion["mensaje"], "catalogo": df_catalogo}
    nuevo_id = siguiente_id(df_catalogo, "ID_Ejemplar", "L")
    nuevo = {
        "ID_Ejemplar": nuevo_id,
        "Titulo": str(titulo).strip(),
        "Autor": str(autor).strip(),
        "ISBN": str(isbn).strip(),
        "Categoria_Libro": categoria,
        "Sede": sede,
        "Stock": int(stock),
        "Fecha_Publicacion": validacion["fecha"],
    }
    catalogo = pd.concat([df_catalogo, pd.DataFrame([nuevo])], ignore_index=True)
    return {
        "ok": True,
        "mensaje": config.MENSAJES["libro_dado_de_alta"],
        "ID_Ejemplar": nuevo_id,
        "catalogo": catalogo,
    }


def editar_ejemplar(df_catalogo, id_ejemplar, nuevos_datos):
    catalogo = df_catalogo.copy()
    filtro = catalogo["ID_Ejemplar"] == id_ejemplar
    if not filtro.any():
        return {"ok": False, "mensaje": config.MENSAJES["libro_inexistente"], "catalogo": catalogo, "avisos": []}
    avisos = []
    for columna, valor in nuevos_datos.items():
        if columna == "ID_Ejemplar":
            avisos.append(config.MENSAJES["id_protegido"])
            continue
        catalogo.loc[filtro, columna] = valor
    return {
        "ok": True,
        "mensaje": "✅ Ejemplar actualizado",
        "avisos": avisos,
        "catalogo": catalogo,
    }


def demoras_previas_de(df_prestamos, id_usuario):
    propios = df_prestamos[df_prestamos["ID_Usuario"] == id_usuario]
    if propios.empty:
        return 0
    devueltos = propios.dropna(subset=["Fecha_Devolucion_Real"])
    if devueltos.empty:
        return 0
    demora = (
        pd.to_datetime(devueltos["Fecha_Devolucion_Real"])
        - pd.to_datetime(devueltos["Fecha_Devolucion_Pactada"])
    ).dt.days
    return int((demora > 0).sum())


def registrar_reserva(df_usuarios, df_catalogo, df_prestamos, id_usuario, id_ejemplar, dias, fecha_prestamo=None):
    respuesta = {
        "ok": False,
        "mensaje": "",
        "usuarios": df_usuarios,
        "catalogo": df_catalogo,
        "prestamos": df_prestamos,
    }
    usuario = obtener_usuario(df_usuarios, id_usuario)
    if usuario is None:
        respuesta["mensaje"] = config.MENSAJES["usuario_inexistente"]
        return respuesta
    ejemplar = obtener_ejemplar(df_catalogo, id_ejemplar)
    if ejemplar is None:
        respuesta["mensaje"] = config.MENSAJES["libro_inexistente"]
        return respuesta
    if esta_sancionado(df_usuarios, id_usuario):
        respuesta["mensaje"] = config.MENSAJES["usuario_sancionado"]
        return respuesta
    if not hay_stock(df_catalogo, id_ejemplar):
        respuesta["mensaje"] = config.MENSAJES["sin_stock"]
        return respuesta
    validacion = validar_dias_prestamo(dias)
    if not validacion["ok"]:
        respuesta["mensaje"] = validacion["mensaje"]
        return respuesta

    if fecha_prestamo is not None:
        fecha_prestamo = pd.to_datetime(fecha_prestamo)
    else:
        fecha_prestamo = pd.Timestamp.today().normalize()
    fecha_pactada = calcular_fecha_devolucion(fecha_prestamo, validacion["dias"])
    nuevo = {
        "ID_Prestamo": siguiente_id(df_prestamos, "ID_Prestamo", "P"),
        "ID_Usuario": id_usuario,
        "ID_Ejemplar": id_ejemplar,
        "Tipo_Usuario": usuario["Tipo_Usuario"],
        "Categoria_Libro": ejemplar["Categoria_Libro"],
        "Sede": usuario["Sede"],
        "Fecha_Prestamo": fecha_prestamo,
        "Fecha_Devolucion_Pactada": fecha_pactada,
        "Fecha_Devolucion_Real": pd.NaT,
        "Demoras_Previas": demoras_previas_de(df_prestamos, id_usuario),
    }
    prestamos = pd.concat([df_prestamos, pd.DataFrame([nuevo])], ignore_index=True)
    catalogo = df_catalogo.copy()
    catalogo.loc[catalogo["ID_Ejemplar"] == id_ejemplar, "Stock"] = int(ejemplar["Stock"]) - 1
    confirmacion = config.MENSAJES["reserva_confirmada"]
    vencimiento = fecha_pactada.strftime(config.FORMATO_FECHA)

    respuesta.update(
        {
            "ok": True,
            "mensaje": f"{confirmacion}: devolver antes del {vencimiento}",
            "prestamo": nuevo,
            "catalogo": catalogo,
            "prestamos": prestamos,
        }
    )
    return respuesta


def registrar_devolucion(df_prestamos, df_catalogo, id_prestamo, fecha_devolucion=None):
    prestamos = df_prestamos.copy()
    filtro = prestamos["ID_Prestamo"] == id_prestamo
    if not filtro.any():
        return {
            "ok": False,
            "mensaje": "❌ Error: el préstamo indicado no existe",
            "prestamos": prestamos,
            "catalogo": df_catalogo,
        }
    if fecha_devolucion is not None:
        fecha_devolucion = pd.to_datetime(fecha_devolucion)
    else:
        fecha_devolucion = pd.Timestamp.today().normalize()
    prestamos.loc[filtro, "Fecha_Devolucion_Real"] = fecha_devolucion
    id_ejemplar = prestamos.loc[filtro, "ID_Ejemplar"].iloc[0]
    catalogo = df_catalogo.copy()
    en_catalogo = catalogo["ID_Ejemplar"] == id_ejemplar
    catalogo.loc[en_catalogo, "Stock"] = catalogo.loc[en_catalogo, "Stock"].astype(int) + 1
    return {"ok": True, "mensaje": "✅ Devolución registrada", "prestamos": prestamos, "catalogo": catalogo}


def prestamos_por_vencer(df_prestamos, fecha_actual=None, dias_de_aviso=None):
    if dias_de_aviso is None:
        dias_de_aviso = config.DIAS_DE_AVISO_PREVIO
    if fecha_actual is not None:
        fecha_actual = pd.to_datetime(fecha_actual)
    else:
        fecha_actual = pd.Timestamp.today().normalize()
    vigentes = df_prestamos[df_prestamos["Fecha_Devolucion_Real"].isna()].copy()
    vigentes["Fecha_Devolucion_Pactada"] = pd.to_datetime(
        vigentes["Fecha_Devolucion_Pactada"], errors="coerce", dayfirst=True
    )
    faltan = (vigentes["Fecha_Devolucion_Pactada"] - fecha_actual).dt.days
    return vigentes[(faltan >= 0) & (faltan <= dias_de_aviso)]


def generar_notificacion_vencimiento(prestamo, df_usuarios, df_catalogo, nivel_riesgo=None):
    usuario = obtener_usuario(df_usuarios, prestamo["ID_Usuario"])
    ejemplar = obtener_ejemplar(df_catalogo, prestamo["ID_Ejemplar"])
    fecha_limite = pd.to_datetime(prestamo["Fecha_Devolucion_Pactada"], errors="coerce", dayfirst=True)
    if pd.isna(fecha_limite):
        return {"ok": False, "mensaje": "❌ Error: el préstamo no tiene una fecha de devolución válida"}
    titulo = ejemplar["Titulo"] if ejemplar is not None else "Ejemplar sin datos"
    nombre = usuario["Nombre"] if usuario is not None else "Usuario"
    correo = usuario["Email"] if usuario is not None else "sin-correo@ispc.edu.ar"
    vencimiento = fecha_limite.strftime(config.FORMATO_FECHA)
    cuerpo = [
        f"Para: {correo}",
        "Asunto: BiblioTech - Recordatorio de devolución",
        "",
        f"Hola {nombre}:",
        f"Te recordamos que el ejemplar «{titulo}» debe devolverse antes del {vencimiento}.",
    ]
    if nivel_riesgo == "ALTO":
        cuerpo.append(
            "Este aviso se envía de forma anticipada porque el préstamo figura con riesgo alto de demora."
        )
    cuerpo.append("Biblioteca ISPC")
    return {
        "ok": True,
        "destinatario": correo,
        "fecha_limite": fecha_limite,
        "mensaje": "\n".join(cuerpo),
    }
