from flet import (ButtonStyle, Column, Container, Control, IconButton, Page, PopupMenuButton, PopupMenuItem, Row,
                  RoundedRectangleBorder, Text, TextButton, TextField, border, border_radius, colors, icons, padding)
from src.board import Board
from src.data_store import DataStore
from src.sidebar import Sidebar
from custom.colores import Colores
from custom.textos import Textos
from custom.tamanos import Tamanos
from custom.iconos import Iconos

class AppLayout(Row):
    def __init__(self, app, page: Page, store: DataStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.page = page
        self.page.on_resize = self.page_resize
        self.store: DataStore = store
        self.toggle_nav_rail_button = IconButton(icon=Iconos.nav_rail_izquierdo,icon_color=Colores.btn_regresar,
                                                 selected=False,selected_icon=Iconos.nav_rail_derecho,
                                                 selected_icon_color=Colores.btn_regresar,on_click=self.toggle_nav_rail,)
        self.sidebar = Sidebar(self, self.store, page)
        self.members_view = Container(Text(value = Textos.vista_miembros,
                                           color = Colores.texto_cuerpo,
                                           style="headlineMedium"),
                                      expand=True,
                                      padding=padding.only(top=Tamanos.mis_tableros_padding))
        self.all_boards_view = Column([
            Row([
                Container(
                    Text(value=Textos.vista_tableros,
                         color = Colores.texto_cuerpo,
                         style="headlineMedium"),
                    expand=True,
                    padding=padding.only(top=Tamanos.mis_tableros_padding)),
                Container(
                    TextButton(
                        Textos.nuevo_tablero_add,
                        icon=Iconos.agregar_tablero,
                        on_click=self.app.add_board,
                        style=ButtonStyle(
                            bgcolor={"": Colores.btn_agregar_tablero,"hovered": Colores.btn_agregar_tablero_hoover},
                            shape={"": RoundedRectangleBorder(radius=Tamanos.btn_agregar_tablero_radio)})),
                    padding=padding.only(right=Tamanos.btn_agregar_tablero_padding_R, 
                                         top=Tamanos.btn_agregar_tablero_padding_L))]),
            Row([
                TextField(
                    hint_text=Textos.barra_buscar_tableros,
                    color = Colores.texto_cuerpo,
                    autofocus=False,
                    content_padding=padding.only(left=Tamanos.barra_buscar_tablero_padding),
                    width=Tamanos.barra_buscar_tablero_ancho,
                    height=Tamanos.barra_buscar_tablero_altura,
                    text_size=Tamanos.barra_buscar_tablero_texto,
                    border_color=Colores.barra_buscar_tablero_borde,
                    focused_border_color=Colores.barra_buscar_tablero_focus,
                    suffix_icon=Iconos.barra_buscar_tableros)]),
            Row([Text(Textos.tablero_no_encontrado)])],
            expand=True)
        
        self._active_view: Control = self.all_boards_view
        self.controls = [self.sidebar,self.toggle_nav_rail_button, self.active_view]

    @property
    def active_view(self):
        return self._active_view

    @active_view.setter
    def active_view(self, view):
        self._active_view = view
        self.controls[-1] = self._active_view
        self.sidebar.sync_board_destinations()
        self.update()

    def set_board_view(self, i):
        self.active_view = self.store.get_boards()[i]
        self.sidebar.bottom_nav_rail.selected_index = i
        self.sidebar.top_nav_rail.selected_index = None
        self.sidebar.update()
        self.page.update()
        self.page_resize()

    def set_all_boards_view(self):
        self.active_view = self.all_boards_view
        self.hydrate_all_boards_view()
        self.sidebar.top_nav_rail.selected_index = 0
        self.sidebar.bottom_nav_rail.selected_index = None
        self.sidebar.update()
        self.page.update()

    def set_members_view(self):
        self.active_view = self.members_view
        self.sidebar.top_nav_rail.selected_index = 1
        self.sidebar.bottom_nav_rail.selected_index = None
        self.sidebar.update()
        self.page.update()

    def page_resize(self, e=None):
        if type(self.active_view) is Board:
            self.active_view.resize(
                self.sidebar.visible, self.page.width, self.page.height
            )
        self.page.update()

    def hydrate_all_boards_view(self):
        self.all_boards_view.controls[-1] = Row([Container(
            content=Row([
                Container(
                    content=Text(value=b.name),
                    data=b,
                    expand=True,
                    on_click=self.board_click),
                Container(
                    content=PopupMenuButton(
                        items=[
                            PopupMenuItem(
                                content=Text(value=Textos.btn_eliminar_tablero,
                                             style="labelMedium",
                                             text_align="center"),
                                             on_click=self.app.delete_board,
                                             data=b),
                            PopupMenuItem(),
                            PopupMenuItem(
                                content=Text(
                                    value=Textos.btn_archivar_tablero,
                                    style="labelMedium",
                                    text_align="center"))]),
                        padding=padding.only(right=Tamanos.btnes_accion_tablero_padding),
                        border_radius=border_radius.all(Tamanos.btnes_accion_tablero_radio))],
                alignment="spaceBetween"),
            border=border.all(Tamanos.tablero_borde, colors.BLACK38),
            border_radius=border_radius.all(Tamanos.tablero_borde_radio),
            bgcolor=Colores.tablero_default_fondo,
            padding=padding.all(Tamanos.tablero_padding_all),
            width=Tamanos.tablero_ancho,
            data=b)
            for b in self.store.get_boards()],
            wrap=True,
        )
        self.sidebar.sync_board_destinations()

    def board_click(self, e):
        self.sidebar.bottom_nav_change(
            self.store.get_boards().index(e.control.data))

    def toggle_nav_rail(self, e):
        self.sidebar.visible = not self.sidebar.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.page_resize()
        self.page.update()
