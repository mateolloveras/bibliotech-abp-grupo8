import ipywidgets as widgets
import pandas as pd
from IPython.display import clear_output, display

from src import config, eda, modelo as modelo_ml, negocio


class AplicacionBiblioTech:
    def __init__(self, df_prestamos, df_usuarios, df_catalogo, modelo_entrenado, metricas=None):
        self.prestamos = df_prestamos
        self.usuarios = df_usuarios
        self.catalogo = df_catalogo
        self.modelo = modelo_entrenado
        self.metricas = metricas or {}
        self.sesion = negocio.cerrar_sesion()

    def categorias_disponibles(self):
        return ["Todas"] + sorted(self.catalogo["Categoria_Libro"].unique().tolist())

    def sedes_disponibles(self):
        return sorted(self.usuarios["Sede"].unique().tolist())

    def panel_login(self):
        email = widgets.Text(description="Usuario:", placeholder="correo@ispc.edu.ar")
        clave = widgets.Password(description="Clave:")
        ingresar = widgets.Button(description="Ingresar", button_style="success", icon="sign-in")
        salir = widgets.Button(description="Cerrar Sesión", button_style="warning")
        salida = widgets.Output()

        def al_ingresar(_):
            with salida:
                clear_output()
                respuesta = negocio.autenticar(self.usuarios, email.value, clave.value)
                if respuesta["ok"]:
                    self.sesion = respuesta["sesion"]
                print(respuesta["mensaje"])

        def al_salir(_):
            with salida:
                clear_output()
                self.sesion = negocio.cerrar_sesion()
                print("Sesión cerrada. Ingrese nuevamente sus credenciales.")

        ingresar.on_click(al_ingresar)
        salir.on_click(al_salir)
        return widgets.VBox(
            [
                widgets.HTML("<h3>Acceso al sistema</h3>"),
                email,
                clave,
                widgets.HBox([ingresar, salir]),
                salida,
            ]
        )

    def panel_catalogo(self):
        termino = widgets.Text(description="Buscar:", placeholder="Título, autor o ISBN")
        categoria = widgets.Dropdown(options=self.categorias_disponibles(), description="Categoría:")
        buscar = widgets.Button(description="Buscar", button_style="info", icon="search")
        salida = widgets.Output()

        def al_buscar(_):
            with salida:
                clear_output()
                respuesta = negocio.buscar_en_catalogo(self.catalogo, termino.value, categoria.value)
                for aviso in respuesta["avisos"]:
                    print(aviso)
                resultados = respuesta["resultados"]
                if resultados.empty:
                    print("No se encontraron ejemplares para la búsqueda indicada.")
                else:
                    print(f"{len(resultados)} ejemplar(es) encontrado(s)")
                    display(
                        resultados[
                            ["ID_Ejemplar", "Titulo", "Autor", "Categoria_Libro", "Sede", "Stock"]
                        ].head(20)
                    )

        buscar.on_click(al_buscar)
        return widgets.VBox(
            [
                widgets.HTML("<h3>Catálogo bibliográfico</h3>"),
                widgets.HBox([termino, categoria, buscar]),
                salida,
            ]
        )

    def panel_reservas(self):
        usuario = widgets.Dropdown(
            options=self._opciones_usuarios(), description="Usuario:", layout=widgets.Layout(width="420px")
        )
        ejemplar = widgets.Dropdown(
            options=self._opciones_catalogo(), description="Ejemplar:", layout=widgets.Layout(width="420px")
        )
        dias = widgets.BoundedIntText(value=7, min=0, max=30, description="Días:")
        confirmar = widgets.Button(description="Confirmar Reserva", button_style="success", icon="check")
        salida = widgets.Output()

        def al_confirmar(_):
            with salida:
                clear_output()
                respuesta = negocio.registrar_reserva(
                    self.usuarios, self.catalogo, self.prestamos, usuario.value, ejemplar.value, dias.value
                )
                print(respuesta["mensaje"])
                if respuesta["ok"]:
                    self.prestamos = respuesta["prestamos"]
                    self.catalogo = respuesta["catalogo"]
                    prestamo = respuesta["prestamo"]
                    riesgo = modelo_ml.predecir_riesgo(
                        self.modelo,
                        prestamo["Categoria_Libro"],
                        prestamo["Tipo_Usuario"],
                        prestamo["Demoras_Previas"],
                        prestamo["Sede"],
                    )
                    print(riesgo["mensaje"])
                    if riesgo["nivel"] == "ALTO":
                        aviso = negocio.generar_notificacion_vencimiento(
                            prestamo, self.usuarios, self.catalogo, riesgo["nivel"]
                        )
                        print("")
                        print(aviso["mensaje"])
                    ejemplar.options = self._opciones_catalogo()

        confirmar.on_click(al_confirmar)
        return widgets.VBox(
            [
                widgets.HTML("<h3>Reserva de ejemplares</h3>"),
                usuario,
                ejemplar,
                dias,
                confirmar,
                salida,
            ]
        )

    def panel_usuarios(self):
        nombre = widgets.Text(description="Nombre:")
        correo = widgets.Text(description="Email:")
        rol = widgets.Dropdown(options=["Estudiante", "Docente", "Bibliotecario"], description="Rol:")
        sede = widgets.Dropdown(options=self.sedes_disponibles(), description="Sede:")
        guardar = widgets.Button(description="Guardar", button_style="success", icon="save")
        termino = widgets.Text(description="Buscar:")
        buscar = widgets.Button(description="Buscar", button_style="info", icon="search")
        salida = widgets.Output()

        def al_guardar(_):
            with salida:
                clear_output()
                respuesta = negocio.registrar_usuario(
                    self.usuarios, nombre.value, correo.value, rol.value, sede=sede.value
                )
                print(respuesta["mensaje"])
                if respuesta["ok"]:
                    self.usuarios = respuesta["usuarios"]
                    print(f"ID asignado: {respuesta['ID_Usuario']}")

        def al_buscar(_):
            with salida:
                clear_output()
                encontrados = negocio.buscar_usuario(self.usuarios, termino.value)
                if encontrados.empty:
                    print("No se encontraron usuarios con ese criterio.")
                else:
                    display(encontrados[["ID_Usuario", "Nombre", "Email", "Rol", "Sede", "Estado"]])

        guardar.on_click(al_guardar)
        buscar.on_click(al_buscar)
        return widgets.VBox(
            [
                widgets.HTML("<h3>Gestión de usuarios</h3>"),
                nombre,
                correo,
                rol,
                sede,
                guardar,
                widgets.HBox([termino, buscar]),
                salida,
            ]
        )

    def panel_prediccion(self):
        categoria = widgets.Dropdown(
            options=sorted(self.catalogo["Categoria_Libro"].unique().tolist()), description="Categoría:"
        )
        tipo = widgets.Dropdown(options=["Alumno", "Docente"], description="Tipo:")
        sede = widgets.Dropdown(options=self.sedes_disponibles(), description="Sede:")
        demoras = widgets.BoundedIntText(value=0, min=0, max=15, description="Demoras:")
        calcular = widgets.Button(description="Calcular riesgo de mora", button_style="danger", icon="bolt")
        salida = widgets.Output()

        def al_calcular(_):
            with salida:
                clear_output()
                riesgo = modelo_ml.predecir_riesgo(
                    self.modelo, categoria.value, tipo.value, demoras.value, sede.value
                )
                print(riesgo["mensaje"])
                if riesgo["nivel"] == "ALTO":
                    print("Acción sugerida: enviar recordatorio preventivo antes del vencimiento.")

        calcular.on_click(al_calcular)
        return widgets.VBox(
            [
                widgets.HTML("<h3>Predicción de riesgo de mora</h3>"),
                categoria,
                tipo,
                sede,
                demoras,
                calcular,
                salida,
            ]
        )

    def panel_dashboard(self):
        actualizar = widgets.Button(description="Actualizar dashboard", button_style="primary", icon="refresh")
        salida = widgets.Output()

        def al_actualizar(_):
            with salida:
                clear_output()
                print(eda.imprimir_resumen(self.prestamos))
                if self.metricas:
                    print("")
                    print(
                        "Modelo de Regresión Logística -> "
                        f"Accuracy: {self.metricas['accuracy']} | "
                        f"Precisión: {self.metricas['precision']} | "
                        f"Recall: {self.metricas['recall']}"
                    )
                eda.grafico_dias_de_prestamo(self.prestamos, mostrar=True)
                eda.grafico_categorias(self.prestamos, mostrar=True)
                eda.grafico_mora_por_sede(self.prestamos, mostrar=True)

        actualizar.on_click(al_actualizar)
        return widgets.VBox([widgets.HTML("<h3>Dashboard de indicadores</h3>"), actualizar, salida])

    def panel_notificaciones(self):
        fecha = widgets.DatePicker(description="Fecha:", value=pd.Timestamp.today().date())
        generar = widgets.Button(description="Verificar vencimientos", button_style="warning", icon="envelope")
        salida = widgets.Output()

        def al_generar(_):
            with salida:
                clear_output()
                proximos = negocio.prestamos_por_vencer(self.prestamos, fecha.value)
                if proximos.empty:
                    print("No hay préstamos próximos a vencer para la fecha indicada.")
                    return
                print(f"{len(proximos)} préstamo(s) por vencer en los próximos {config.DIAS_DE_AVISO_PREVIO} días")
                for _, prestamo in proximos.head(5).iterrows():
                    riesgo = modelo_ml.predecir_riesgo(
                        self.modelo,
                        prestamo["Categoria_Libro"],
                        prestamo["Tipo_Usuario"],
                        prestamo["Demoras_Previas"],
                        prestamo["Sede"],
                    )
                    aviso = negocio.generar_notificacion_vencimiento(
                        prestamo, self.usuarios, self.catalogo, riesgo["nivel"]
                    )
                    print("")
                    print(aviso["mensaje"])

        generar.on_click(al_generar)
        return widgets.VBox(
            [widgets.HTML("<h3>Simulador de notificaciones</h3>"), fecha, generar, salida]
        )

    def _opciones_usuarios(self):
        activos = self.usuarios.sort_values("ID_Usuario")
        return [
            (f"{fila['ID_Usuario']} - {fila['Nombre']} ({fila['Estado']})", fila["ID_Usuario"])
            for _, fila in activos.iterrows()
        ]

    def _opciones_catalogo(self):
        return [
            (f"{fila['ID_Ejemplar']} - {fila['Titulo']} (Stock: {fila['Stock']})", fila["ID_Ejemplar"])
            for _, fila in self.catalogo.iterrows()
        ]

    def mostrar(self):
        pestanas = widgets.Tab(
            children=[
                self.panel_login(),
                self.panel_catalogo(),
                self.panel_reservas(),
                self.panel_usuarios(),
                self.panel_prediccion(),
                self.panel_notificaciones(),
                self.panel_dashboard(),
            ]
        )
        titulos = [
            "Login",
            "Catálogo",
            "Reservas",
            "Usuarios",
            "Riesgo de mora",
            "Notificaciones",
            "Dashboard",
        ]
        for posicion, titulo in enumerate(titulos):
            pestanas.set_title(posicion, titulo)
        return pestanas
