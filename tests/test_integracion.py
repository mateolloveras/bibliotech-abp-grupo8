import time
import unittest

import numpy as np
import pandas as pd

from src import config, datos, modelo, negocio


class PruebasDeIntegracion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prestamos = datos.cargar_prestamos()
        cls.usuarios = datos.cargar_usuarios()
        cls.catalogo = datos.cargar_catalogo()
        cls.modelo, cls.metricas = modelo.entrenar_modelo(cls.prestamos)

    def test_pi01_interfaz_filtra_el_catalogo(self):
        respuesta = negocio.buscar_en_catalogo(self.catalogo, "", "Informática")
        resultados = respuesta["resultados"]
        self.assertGreater(len(resultados), 0)
        self.assertEqual(resultados["Categoria_Libro"].unique().tolist(), ["Informática"])
        self.assertEqual(len(resultados), len(resultados.drop_duplicates(subset="ID_Ejemplar")))

    def test_pi02_la_reserva_sincroniza_prestamos_y_catalogo(self):
        catalogo = self.catalogo.copy()
        catalogo.loc[catalogo["ID_Ejemplar"] == "L-003", "Stock"] = 1
        respuesta = negocio.registrar_reserva(
            self.usuarios, catalogo, self.prestamos, "U-005", "L-003", 7
        )
        self.assertTrue(respuesta["ok"])
        self.assertEqual(len(respuesta["prestamos"]), len(self.prestamos) + 1)
        actualizado = negocio.obtener_ejemplar(respuesta["catalogo"], "L-003")
        self.assertEqual(int(actualizado["Stock"]), 0)
        ultimo = respuesta["prestamos"].iloc[-1]
        self.assertEqual(ultimo["ID_Ejemplar"], "L-003")
        self.assertTrue(pd.isna(ultimo["Fecha_Devolucion_Real"]))

    def test_pi03_el_modelo_tolera_categorias_nulas(self):
        lote = pd.DataFrame(
            [
                {
                    "Categoria_Libro": "Informática",
                    "Tipo_Usuario": "Alumno",
                    "Sede": "Cosquín",
                    "Demoras_Previas": 2,
                },
                {
                    "Categoria_Libro": np.nan,
                    "Tipo_Usuario": "Alumno",
                    "Sede": "Cosquín",
                    "Demoras_Previas": 4,
                },
                {
                    "Categoria_Libro": "Categoría Inexistente",
                    "Tipo_Usuario": "Docente",
                    "Sede": "Villa María",
                    "Demoras_Previas": 0,
                },
            ]
        )
        resultado = modelo.predecir_lote(self.modelo, lote)
        self.assertEqual(len(resultado), 3)
        self.assertTrue(resultado["Probabilidad_Mora"].between(0, 1).all())
        self.assertTrue(resultado["Nivel_Riesgo"].isin(["BAJO", "MEDIO", "ALTO"]).all())

    def test_pi04_el_riesgo_alto_dispara_la_notificacion(self):
        riesgo = modelo.predecir_riesgo(self.modelo, "Informática", "Alumno", 6, "Cosquín")
        self.assertEqual(riesgo["nivel"], "ALTO")
        prestamo = {
            "ID_Usuario": "U-089",
            "ID_Ejemplar": "L-014",
            "Fecha_Devolucion_Pactada": pd.Timestamp("2026-10-28"),
        }
        aviso = negocio.generar_notificacion_vencimiento(
            prestamo, self.usuarios, self.catalogo, riesgo["nivel"]
        )
        self.assertTrue(aviso["ok"])
        self.assertIn("@ispc.edu.ar", aviso["destinatario"])
        self.assertIn("28/10/2026", aviso["mensaje"])
        self.assertIn("riesgo alto", aviso["mensaje"])

    def test_flujo_completo_de_punta_a_punta(self):
        catalogo = self.catalogo.copy()
        usuarios = self.usuarios.copy()
        prestamos = self.prestamos.copy()

        sesion = negocio.autenticar(usuarios, "gino.lencina@ispc.edu.ar", "Biblio2026*")
        self.assertTrue(sesion["ok"])

        alta = negocio.registrar_usuario(usuarios, "Juan Pérez", "jperez@ispc.edu.ar", "Estudiante")
        usuarios = alta["usuarios"]

        busqueda = negocio.buscar_en_catalogo(catalogo, "Python")
        self.assertGreater(len(busqueda["resultados"]), 0)
        id_ejemplar = busqueda["resultados"].iloc[0]["ID_Ejemplar"]

        reserva = negocio.registrar_reserva(
            usuarios, catalogo, prestamos, alta["ID_Usuario"], id_ejemplar, 14
        )
        self.assertTrue(reserva["ok"])
        prestamo = reserva["prestamo"]

        inicio = time.time()
        riesgo = modelo.predecir_riesgo(
            self.modelo,
            prestamo["Categoria_Libro"],
            prestamo["Tipo_Usuario"],
            prestamo["Demoras_Previas"],
            prestamo["Sede"],
        )
        self.assertLess(time.time() - inicio, 2)

        aviso = negocio.generar_notificacion_vencimiento(
            prestamo, usuarios, reserva["catalogo"], riesgo["nivel"]
        )
        self.assertTrue(aviso["ok"])
        self.assertIn(config.MENSAJES["reserva_confirmada"], reserva["mensaje"])


if __name__ == "__main__":
    unittest.main()
