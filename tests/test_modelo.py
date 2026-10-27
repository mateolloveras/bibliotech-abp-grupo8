import time
import unittest

from src import config, datos, modelo

METRICAS_DOCUMENTADAS = {"accuracy": 0.78, "precision": 0.71, "recall": 0.65}


class PruebasDelModeloPredictivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prestamos = datos.cargar_prestamos()
        cls.modelo, cls.metricas = modelo.entrenar_modelo(cls.prestamos)

    def test_metricas_reproducen_los_valores_informados(self):
        self.assertEqual(self.metricas["accuracy"], METRICAS_DOCUMENTADAS["accuracy"])
        self.assertEqual(self.metricas["precision"], METRICAS_DOCUMENTADAS["precision"])
        self.assertEqual(self.metricas["recall"], METRICAS_DOCUMENTADAS["recall"])

    def test_meta3_accuracy_superior_a_075(self):
        self.assertGreater(self.metricas["accuracy"], 0.75)

    def test_bt06_prediccion_de_riesgo_alto(self):
        riesgo = modelo.predecir_riesgo(self.modelo, "Informática", "Alumno", 3)
        self.assertEqual(riesgo["nivel"], "ALTO")
        self.assertGreaterEqual(riesgo["probabilidad"], config.UMBRAL_RIESGO_ALTO)
        self.assertIn("Probabilidad estimada de mora", riesgo["mensaje"])

    def test_clasificacion_por_umbrales(self):
        self.assertEqual(modelo.clasificar_riesgo(0.95), "ALTO")
        self.assertEqual(modelo.clasificar_riesgo(0.70), "ALTO")
        self.assertEqual(modelo.clasificar_riesgo(0.55), "MEDIO")
        self.assertEqual(modelo.clasificar_riesgo(0.40), "MEDIO")
        self.assertEqual(modelo.clasificar_riesgo(0.12), "BAJO")

    def test_meta3_inferencia_menor_a_dos_segundos(self):
        inicio = time.time()
        modelo.predecir_riesgo(self.modelo, "Ciencias Sociales", "Docente", 1, "Villa María")
        self.assertLess(time.time() - inicio, 2)

    def test_el_historial_de_demoras_aumenta_el_riesgo(self):
        sin_historial = modelo.predecir_riesgo(self.modelo, "Informática", "Alumno", 0)
        con_historial = modelo.predecir_riesgo(self.modelo, "Informática", "Alumno", 5)
        self.assertLess(sin_historial["probabilidad"], con_historial["probabilidad"])

    def test_el_pipeline_incluye_imputacion_y_codificacion(self):
        pasos = dict(modelo.construir_pipeline().named_steps)
        self.assertIn("preprocesamiento", pasos)
        self.assertIn("clasificador", pasos)
        transformadores = dict(
            (nombre, transformador)
            for nombre, transformador, _ in pasos["preprocesamiento"].transformers
        )
        categoricas = dict(transformadores["categoricas"].named_steps)
        self.assertEqual(categoricas["imputacion"].strategy, "constant")
        self.assertEqual(categoricas["imputacion"].fill_value, config.CATEGORIA_POR_DEFECTO)
        self.assertEqual(categoricas["codificacion"].handle_unknown, "ignore")


if __name__ == "__main__":
    unittest.main()
