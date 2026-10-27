import unittest

from src import config, datos, eda


class PruebasDeCalidadDeDatos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prestamos = datos.cargar_prestamos()
        cls.usuarios = datos.cargar_usuarios()
        cls.catalogo = datos.cargar_catalogo()

    def test_rf1_el_dataset_se_carga_con_las_columnas_esperadas(self):
        esperadas = [
            "ID_Prestamo",
            "ID_Usuario",
            "ID_Ejemplar",
            "Tipo_Usuario",
            "Categoria_Libro",
            "Sede",
            "Fecha_Prestamo",
            "Fecha_Devolucion_Pactada",
            "Fecha_Devolucion_Real",
            "Demoras_Previas",
        ]
        self.assertEqual(list(self.prestamos.columns), esperadas)
        self.assertGreater(len(self.prestamos), 800)

    def test_rf2_no_hay_registros_duplicados(self):
        self.assertEqual(datos.controlar_calidad(self.prestamos)["duplicados"], 0)
        self.assertEqual(datos.controlar_calidad(self.usuarios)["duplicados"], 0)
        self.assertEqual(datos.controlar_calidad(self.catalogo)["duplicados"], 0)

    def test_rf2_los_nulos_solo_aparecen_en_la_devolucion_real(self):
        columnas_con_nulos = datos.controlar_calidad(self.prestamos)["columnas_con_nulos"]
        self.assertEqual(list(columnas_con_nulos.keys()), ["Fecha_Devolucion_Real"])

    def test_los_prestamos_vigentes_se_excluyen_del_calculo_de_demora(self):
        cerrados, vigentes, extraviados = datos.separar_por_estado(self.prestamos)
        self.assertGreater(len(vigentes), 0)
        self.assertEqual(cerrados["Dias_Demora"].isna().sum(), 0)
        self.assertTrue((extraviados["Dias_Demora"] > config.DIAS_PARA_CONSIDERAR_EXTRAVIO).all())
        self.assertEqual(len(cerrados) + len(vigentes) + len(extraviados), len(self.prestamos))

    def test_conclusiones_del_eda(self):
        resumen = eda.resumen_ejecutivo(self.prestamos)
        self.assertEqual(resumen["promedio_dias_demora"], 4.0)
        self.assertEqual(resumen["categoria_top"], "Informática")
        self.assertEqual(resumen["segunda_categoria"], "Ciencias Sociales")
        self.assertEqual(resumen["sede_con_mas_prestamos"], "Cosquín")
        self.assertEqual(resumen["sede_con_mas_mora"], "Cosquín")

    def test_datos_de_prueba_de_los_casos_funcionales(self):
        suspendido = self.usuarios[self.usuarios["ID_Usuario"] == "U-012"].iloc[0]
        sin_stock = self.catalogo[self.catalogo["ID_Ejemplar"] == "L-205"].iloc[0]
        self.assertEqual(suspendido["Estado"], config.ESTADO_SUSPENDIDO)
        self.assertEqual(int(sin_stock["Stock"]), 0)
        self.assertEqual(len(self.usuarios), 103)

    def test_la_tabla_del_modelo_no_tiene_valores_nulos(self):
        tabla = datos.datos_para_modelo(self.prestamos)
        self.assertEqual(int(tabla.isna().sum().sum()), 0)
        self.assertTrue(tabla[config.COLUMNA_OBJETIVO].isin([0, 1]).all())


if __name__ == "__main__":
    unittest.main()
