import flet
from flet import (
    AlertDialog,
    AppBar,
    Column,
    Container,
    ElevatedButton,
    Icon,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    RoundedRectangleBorder,
    Row,
    TemplateRoute,
    Text,
    TextField,
    UserControl,
    View,
    colors,
    icons,
    margin,
    padding,
    theme,
)
from src.memory_store import InMemoryStore
from src.user import User
from src.app_layout import AppLayout
from src.board import Board
from src.data_store import DataStore




class Textos:
    titulo_app = "Flet Kanban App"
    login = "Log-in"
    configuraciones = "Configuraciones"
    titulo_appBar = "Kanban"
    fuente_base = "Pacifico"
    encabezado_tablero_demo = "Tablero Demo"
    nuevo_usuario = "Ingrese su Usuario"
    nuevo_password = "Ingrese su contraseña"
    encabezado_nuevo_usuario = "Por favor ingrese su usuario y contraseña/password"
    nuevo_tablero_nombre = "Nombre de Tablero Nuevo"
    nuevo_tablero_boton_crear = "Crear"
    encabezado_dialogo_nuevo_tablero = "Nombra tu nuevo tablero"
    cerrando_modal = "Cerrando Modal"
    boton_cerrar_modal = "Cancelar"
    campo_nuevo_usuario = "Usuario"
    campo_nuevo_password = "Contraseña"


class Colores:
    blue_grey_200 = colors.BLUE_GREY_200
    fondo_pagina = colors.BLUE_GREY_200
    boton_crear_tablero = colors.BLUE_200
    bgc_appBar = colors.LIGHT_BLUE_ACCENT_700


class Iconos:
    appBar = icons.GRID_GOLDENRATIO_ROUNDED


class Tamanos:
    appBar = 100
    tamano_appBar = 32
    altura_appBar = 75

class Rutas:
    home = "/"


class Entorno:
    usuario_actual = "current_user"


class TrelloApp(UserControl):
    def __init__(self, page: Page, store: DataStore):
        super().__init__()
        self.page = page
        self.store: DataStore = store
        self.page.on_route_change = self.route_change
        self.boards = self.store.get_boards()
        self.login_profile_button = PopupMenuItem(text=Textos.login,
                                                  on_click=self.login)
        self.appbar_items = [self.login_profile_button,
                             PopupMenuItem(),
                             PopupMenuItem(text=Textos.configuraciones)]
        self.appbar = AppBar(title=Text(Textos.titulo_appBar,font_family=Textos.fuente_base,
                                        size=Tamanos.tamano_appBar,text_align="start"),
                            leading=Icon(Iconos.appBar),
                            leading_width=Tamanos.appBar,
                            center_title=False,
                            toolbar_height=Tamanos.altura_appBar,
                            bgcolor=Colores.bgc_appBar,
                            actions=[Container(content=PopupMenuButton(items=self.appbar_items),
                                               margin=margin.only(left=50, right=25))])
        self.page.appbar = self.appbar
        self.page.update()

    def build(self):
        self.layout = AppLayout(self, self.page, self.store, tight=True, expand=True, vertical_alignment="start")
        return self.layout

    def initialize(self):
        self.page.views.clear()
        self.page.views.append(View(Rutas.home, [self.appbar, self.layout], 
                                    padding=padding.all(0), bgcolor=Colores.blue_grey_200))
        self.page.update()
        if len(self.boards) == 0:
            self.create_new_board(Textos.encabezado_tablero_demo)
        self.page.go(Rutas.home)

    def login(self, e):
        def close_dlg(e):
            if user_name.value == "" or password.value == "":
                user_name.error_text = Textos.nuevo_usuario
                password.error_text = Textos.nuevo_password
                self.page.update()
                return
            else:
                user = User(user_name.value, password.value)
                if user not in self.store.get_users():
                    self.store.add_user(user)
                self.user = user_name.value
                self.page.client_storage.set(Entorno.usuario_actual, user_name.value)
            dialog.open = False
            self.appbar_items[0] = PopupMenuItem(text=f"Perfil de {self.page.client_storage.get(Entorno.usuario_actual)}")
            self.page.update()

        user_name = TextField(label=Textos.campo_nuevo_usuario)
        password = TextField(label=Textos.campo_nuevo_password, password=True)
        dialog = AlertDialog(title=Text(Textos.encabezado_nuevo_usuario),
                             content=Column([user_name, password, ElevatedButton(text="Login", on_click=close_dlg)]),
                             on_dismiss=lambda e: print(Textos.cerrando_modal),
                             tight=True)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def route_change(self, e):
        troute = TemplateRoute(self.page.route)
        if troute.match(Rutas.home):
            self.page.go("/boards")
        elif troute.match("/board/:id"):
            if int(troute.id) > len(self.store.get_boards()):
                self.page.go(Rutas.home)
                return
            self.layout.set_board_view(int(troute.id))
        elif troute.match("/boards"):
            self.layout.set_all_boards_view()
        elif troute.match("/members"):
            self.layout.set_members_view()
        self.page.update()

    def add_board(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") 
                and not e.control.text == Textos.boton_cerrar_modal) or (
                    type(e.control) is TextField and e.control.value != ""):
                self.create_new_board(dialog_text.value)
            dialog.open = False
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        dialog_text = TextField(label=Textos.nuevo_tablero_nombre, 
                                on_submit=close_dlg, 
                                on_change=textfield_change)
        create_button = ElevatedButton(text=Textos.nuevo_tablero_boton_crear, 
                                       bgcolor=Colores.boton_crear_tablero, 
                                       on_click=close_dlg, disabled=True)
        dialog = AlertDialog(title=Text(Textos.encabezado_dialogo_nuevo_tablero),
                             content=Column([dialog_text,
                                             Row([ElevatedButton(text=Textos.boton_cerrar_modal, on_click=close_dlg),create_button], 
                                                 alignment="spaceBetween")],
                                                 tight=True),
                                                 on_dismiss=lambda e: print(Textos.cerrando_modal))
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_board(self, board_name):
        new_board = Board(self, self.store, board_name)
        self.store.add_board(new_board)
        self.layout.hydrate_all_boards_view()

    def delete_board(self, e):
        self.store.remove_board(e.control.data)
        self.layout.set_all_boards_view()


def main(page: Page):
    page.title = Textos.titulo_app
    page.padding = 0
    page.theme = theme.Theme(font_family="Verdana")
    page.theme.page_transitions.windows = "cupertino"
    page.fonts = {"Pacifico": "Pacifico-Regular.ttf"}
    page.bgcolor = Colores.fondo_pagina
    app = TrelloApp(page, InMemoryStore())
    page.add(app)
    page.update()
    app.initialize()


flet.app(target=main, assets_dir="../assets")
