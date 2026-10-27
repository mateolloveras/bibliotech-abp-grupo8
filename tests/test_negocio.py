import unittest

import pandas as pd

from src import config, datos, negocio


class PruebasDeReglasDeNegocio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prestamos = datos.cargar_prestamos()
        cls.usuarios = datos.cargar_usuarios()
        cls.catalogo = datos.cargar_catalogo()

    def test_bt01_rango_de_dias_de_prestamo(self):
        self.assertFalse(negocio.validar_dias_prestamo(0)["ok"])
        self.assertTrue(negocio.validar_dias_prestamo(1)["ok"])
        self.assertTrue(negocio.validar_dias_prestamo(14)["ok"])
        self.assertFalse(negocio.validar_dias_prestamo(15)["ok"])
        self.assertEqual(
            negocio.validar_dias_prestamo(15)["mensaje"],
            config.MENSAJES["dias_fuera_de_rango"],
        )

    def test_bt02_bloqueo_de_reserva_por_mora(self):
        respuesta = negocio.registrar_reserva(
            self.usuarios, self.catalogo, self.prestamos, "U-012", "L-001", 7
        )
        self.assertFalse(respuesta["ok"])
        self.assertEqual(respuesta["mensaje"], config.MENSAJES["usuario_sancionado"])

    def test_bt03_longitud_maxima_de_busqueda(self):
        termino_valido = "á" * 100
        termino_excedido = "a" * 101
        sin_aviso = negocio.buscar_en_catalogo(self.catalogo, termino_valido)
        con_aviso = negocio.buscar_en_catalogo(self.catalogo, termino_excedido)
        self.assertEqual(sin_aviso["avisos"], [])
        self.assertIn(config.MENSAJES["busqueda_muy_larga"], con_aviso["avisos"])
        self.assertEqual(len(con_aviso["termino_usado"]), 100)

    def test_bt04_validacion_de_fecha_de_publicacion(self):
        hoy = pd.Timestamp("2026-10-27")
        self.assertTrue(negocio.validar_fecha_publicacion("15/05/2021", hoy=hoy)["ok"])
        self.assertFalse(negocio.validar_fecha_publicacion("31/02/2024", hoy=hoy)["ok"])
        self.assertFalse(negocio.validar_fecha_publicacion("10/12/2030", hoy=hoy)["ok"])

    def test_bt05_el_id_de_ejemplar_es_de_solo_lectura(self):
        respuesta = negocio.editar_ejemplar(
            self.catalogo, "L-001", {"ID_Ejemplar": "L-999", "Stock": 4}
        )
        modificado = negocio.obtener_ejemplar(respuesta["catalogo"], "L-001")
        self.assertIn(config.MENSAJES["id_protegido"], respuesta["avisos"])
        self.assertIsNotNone(modificado)
        self.assertEqual(int(modificado["Stock"]), 4)
        self.assertIsNone(negocio.obtener_ejemplar(respuesta["catalogo"], "L-999"))

    def test_bt07_reserva_sin_stock_disponible(self):
        self.assertFalse(negocio.hay_stock(self.catalogo, "L-205"))
        respuesta = negocio.registrar_reserva(
            self.usuarios, self.catalogo, self.prestamos, "U-005", "L-205", 7
        )
        self.assertFalse(respuesta["ok"])
        self.assertEqual(respuesta["mensaje"], config.MENSAJES["sin_stock"])

    def test_bt08_notificacion_con_fecha_sin_convertir(self):
        prestamo = {
            "ID_Usuario": "U-005",
            "ID_Ejemplar": "L-007",
            "Fecha_Devolucion_Pactada": "05/11/2026",
        }
        aviso = negocio.generar_notificacion_vencimiento(prestamo, self.usuarios, self.catalogo)
        self.assertTrue(aviso["ok"])
        self.assertIn("05/11/2026", aviso["mensaje"])
        self.assertNotIn("None", aviso["mensaje"])

    def test_cf01_crear_usuario_valido(self):
        respuesta = negocio.registrar_usuario(
            self.usuarios, "Juan Pérez", "jperez@ispc.edu.ar", "Estudiante"
        )
        self.assertTrue(respuesta["ok"])
        self.assertEqual(respuesta["ID_Usuario"], "U-104")
        self.assertEqual(respuesta["mensaje"], config.MENSAJES["usuario_creado"])
        self.assertEqual(len(respuesta["usuarios"]), len(self.usuarios) + 1)

    def test_cf02_crear_usuario_sin_campos_obligatorios(self):
        respuesta = negocio.registrar_usuario(self.usuarios, "", "test@ispc.edu.ar", "Estudiante")
        self.assertFalse(respuesta["ok"])
        self.assertEqual(respuesta["mensaje"], config.MENSAJES["nombre_obligatorio"])
        self.assertEqual(len(respuesta["usuarios"]), len(self.usuarios))

    def test_cf03_login_con_credenciales_correctas(self):
        respuesta = negocio.autenticar(self.usuarios, "gino.lencina@ispc.edu.ar", "Biblio2026*")
        self.assertTrue(respuesta["ok"])
        self.assertIn("Bienvenido Gino Lencina", respuesta["mensaje"])
        self.assertEqual(respuesta["sesion"]["Rol"], "Bibliotecario")

    def test_cf04_login_con_clave_incorrecta(self):
        respuesta = negocio.autenticar(self.usuarios, "gino.lencina@ispc.edu.ar", "ClaveErronea123")
        self.assertFalse(respuesta["ok"])
        self.assertEqual(respuesta["mensaje"], config.MENSAJES["credenciales_invalidas"])

    def test_cf05_editar_datos_de_usuario(self):
        creado = negocio.registrar_usuario(
            self.usuarios, "Juan Pérez", "jperez@ispc.edu.ar", "Estudiante"
        )
        respuesta = negocio.editar_usuario(
            creado["usuarios"], "U-104", {"Email": "jperez_nuevo@ispc.edu.ar"}
        )
        actualizado = negocio.obtener_usuario(respuesta["usuarios"], "U-104")
        self.assertTrue(respuesta["ok"])
        self.assertEqual(actualizado["Email"], "jperez_nuevo@ispc.edu.ar")

    @unittest.expectedFailure
    def test_cf06_eliminar_usuario_con_prestamo_activo(self):
        self.assertTrue(negocio.tiene_prestamos_activos(self.prestamos, "U-089"))
        respuesta = negocio.eliminar_usuario(self.usuarios, "U-089")
        self.assertFalse(respuesta["ok"])

    def test_cf07_busqueda_de_usuario(self):
        encontrados = negocio.buscar_usuario(self.usuarios, "Lencina")
        self.assertGreaterEqual(len(encontrados), 1)
        self.assertIn("Gino Lencina", encontrados["Nombre"].tolist())

    def test_cf08_cierre_de_sesion(self):
        sesion = negocio.autenticar(self.usuarios, "gino.lencina@ispc.edu.ar", "Biblio2026*")["sesion"]
        self.assertTrue(sesion["activa"])
        cerrada = negocio.cerrar_sesion(sesion)
        self.assertFalse(cerrada["activa"])
        self.assertIsNone(cerrada["ID_Usuario"])

    def test_calculo_de_fecha_de_devolucion(self):
        fecha = negocio.calcular_fecha_devolucion("2026-10-27", 14)
        self.assertEqual(fecha.strftime(config.FORMATO_FECHA), "10/11/2026")

    def test_alta_de_ejemplar_con_fecha_valida(self):
        respuesta = negocio.dar_de_alta_ejemplar(
            self.catalogo,
            "Testeo de Software: Teoría y Práctica",
            "C. Ahumada",
            "978-987-1234-5",
            "Informática",
            "Cosquín",
            3,
            "15/05/2021",
            hoy=pd.Timestamp("2026-10-27"),
        )
        self.assertTrue(respuesta["ok"])
        self.assertEqual(respuesta["ID_Ejemplar"], "L-206")


if __name__ == "__main__":
    unittest.main()
