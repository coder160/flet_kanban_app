from flet import (UserControl, Column, Container, IconButton, Row, Text, IconButton, NavigationRail, padding,
                  NavigationRailDestination, TextField, alignment, border_radius , colors, icons, margin)
from src.data_store import DataStore
from custom.tamanos import Tamanos
from custom.textos import Textos
from custom.rutas import Rutas
from custom.colores import Colores
from custom.iconos import Iconos    

    
class Sidebar(UserControl):

    def __init__(self, app_layout, store: DataStore, page):
        super().__init__()
        self.store: DataStore = store
        self.app_layout = app_layout
        self.nav_rail_visible = True
        self.top_nav_items = [NavigationRailDestination(label_content=Text(Textos.nav_rail_tableros),label=Textos.nav_rail_tableros,icon=Iconos.nav_rail_tableros,selected_icon=Iconos.nav_rail_tableros_activo),
                              NavigationRailDestination(label_content=Text(Textos.nav_rail_miembros),label=Textos.nav_rail_miembros,icon=Iconos.nav_rail_miembros,selected_icon=Iconos.nav_rail_miembros_activo)]
        self.top_nav_rail = NavigationRail(selected_index=None,label_type="all",on_change=self.top_nav_change,destinations=self.top_nav_items,bgcolor=Colores.nav_rail_top,extended=True,height=110)
        self.bottom_nav_rail = NavigationRail(selected_index=None,label_type="all",on_change=self.bottom_nav_change,extended=True,expand=True,bgcolor=Colores.nav_rail_bottom)
        self.toggle_nav_rail_button = IconButton(Iconos.retroceder)

    def build(self):
        self.view = Container(content=Column([Row([Text(Textos.sidebar_encabezado)], alignment="spaceBetween"),
                                              Container(bgcolor=Colores.sidebar_container_detalles_sup,
                                                        border_radius=border_radius.all(Tamanos.sidebar_container_radioborde),
                                                        height=Tamanos.sidebar_altura,
                                                        alignment=alignment.center_right,
                                                        width=Tamanos.sidebar_ancho),
                                              self.top_nav_rail,
                                              Container(bgcolor=Colores.sidebar_container_detalles_inf,
                                                        border_radius=border_radius.all(Tamanos.sidebar_container_radioborde),
                                                        height=Tamanos.sidebar_altura,
                                                        alignment=alignment.center_right,
                                                        width=Tamanos.sidebar_ancho),
                                              self.bottom_nav_rail], 
                                             tight=True),
                                             padding=padding.all(Tamanos.sidebar_padding_all),
                                             margin=margin.all(Tamanos.sidebar_margin_all),
                                             width=Tamanos.sidebar_total_ancho,
                                             expand=True,
                                             bgcolor=Colores.sidebar_container_fondo,
                                             visible=self.nav_rail_visible)
        return self.view

    def sync_board_destinations(self):
        boards = self.store.get_boards()
        self.bottom_nav_rail.destinations = []
        for i in range(len(boards)):
            b = boards[i]
            self.bottom_nav_rail.destinations.append(NavigationRailDestination(label_content=TextField(value=b.name,
                                                                                                       hint_text=b.name,
                                                                                                       text_size=12,
                                                                                                       read_only=True,
                                                                                                       on_focus=self.board_name_focus,
                                                                                                       on_blur=self.board_name_blur,
                                                                                                       border="none",
                                                                                                       height=50,
                                                                                                       width=150,
                                                                                                       text_align="start",
                                                                                                       data=i),
                                                                               label=b.name,
                                                                               selected_icon=Iconos.flecha_,
                                                                               icon=Iconos.flecha_activa))
        self.view.update()

    def toggle_nav_rail(self, e):
        self.view.visible = not self.view.visible
        self.view.update()
        self.page.update()

    def board_name_focus(self, e):
        e.control.read_only = False
        e.control.border = "outline"
        e.control.update()

    def board_name_blur(self, e):
        self.store.update_board(self.store.get_boards()[e.control.data], {'name': e.control.value})
        self.app_layout.hydrate_all_boards_view()
        e.control.read_only = True
        e.control.border = "none"
        self.page.update()

    def top_nav_change(self, e):
        index = e if (type(e) == int) else e.control.selected_index
        self.bottom_nav_rail.selected_index = None
        self.top_nav_rail.selected_index = index
        self.view.update()
        if index == 0:
            self.page.route = Rutas.tableros
        elif index == 1:
            self.page.route = Rutas.miembros
        self.page.update()

    def bottom_nav_change(self, e):
        index = e if (type(e) == int) else e.control.selected_index
        self.top_nav_rail.selected_index = None
        self.bottom_nav_rail.selected_index = index
        self.page.route = f"{Rutas.tablero}/{index}"
        self.view.update()
        self.page.update()