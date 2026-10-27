from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data"
CARPETA_EVIDENCIAS = RAIZ_PROYECTO / "docs" / "evidencias"

ARCHIVO_PRESTAMOS = CARPETA_DATOS / "prestamos_historicos.csv"
ARCHIVO_USUARIOS = CARPETA_DATOS / "usuarios.csv"
ARCHIVO_CATALOGO = CARPETA_DATOS / "catalogo.csv"

SEMILLA = 2026
SEMILLA_PARTICION = 6763
PROPORCION_PRUEBA = 0.25
FORMATO_FECHA = "%d/%m/%Y"

DIAS_MINIMOS_PRESTAMO = 1
DIAS_MAXIMOS_PRESTAMO = 14
LONGITUD_MAXIMA_BUSQUEDA = 100
DIAS_PARA_CONSIDERAR_EXTRAVIO = 90
DIAS_DE_AVISO_PREVIO = 2

ESTADO_ACTIVO = "Activo"
ESTADO_SUSPENDIDO = "Suspendido"
CATEGORIA_POR_DEFECTO = "General"

UMBRAL_RIESGO_ALTO = 0.70
UMBRAL_RIESGO_MEDIO = 0.40

COLUMNAS_CATEGORICAS = ["Categoria_Libro", "Tipo_Usuario", "Sede"]
COLUMNAS_NUMERICAS = ["Demoras_Previas"]
COLUMNA_OBJETIVO = "Devolucion_Tardia"

MENSAJES = {
    "dias_fuera_de_rango": "El plazo de préstamo debe ser de entre 1 y 14 días corridos",
    "usuario_sancionado": "🚫 Operación no permitida: registra una penalización activa. Acérquese a biblioteca",
    "sin_stock": "❌ Sin disponibilidad de ejemplares físicos para este título",
    "reserva_confirmada": "✅ Reserva confirmada",
    "usuario_creado": "✅ Usuario registrado con éxito",
    "nombre_obligatorio": "❌ Error: El campo Nombre es obligatorio",
    "email_obligatorio": "❌ Error: El campo Email es obligatorio",
    "credenciales_invalidas": "❌ Error de autenticación: credenciales inválidas",
    "usuario_actualizado": "✅ Datos actualizados correctamente",
    "usuario_eliminado": "✅ Usuario eliminado del padrón",
    "usuario_inexistente": "❌ Error: el usuario indicado no existe en el padrón",
    "libro_inexistente": "❌ Error: el ejemplar indicado no existe en el catálogo",
    "busqueda_muy_larga": "⚠ El término de búsqueda supera los 100 caracteres permitidos: se truncó al máximo",
    "fecha_invalida": "❌ Error: la fecha ingresada no existe en el calendario",
    "fecha_futura": "❌ Error: la fecha de publicación no puede ser posterior al día de hoy",
    "id_protegido": "⚠ El campo ID_Ejemplar es de solo lectura y no admite modificaciones",
    "libro_dado_de_alta": "✅ Ejemplar dado de alta en el catálogo",
}

ETIQUETAS_RIESGO = {
    "ALTO": "🔴 RIESGO ALTO (Priorizar recordatorio)",
    "MEDIO": "🟡 RIESGO MEDIO (Seguimiento habitual)",
    "BAJO": "🟢 RIESGO BAJO (Sin acción preventiva)",
}
