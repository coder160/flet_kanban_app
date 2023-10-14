from flet import (UserControl, Draggable, DragTarget, Column, Row, Text, Icon, PopupMenuButton, PopupMenuItem,
                  Container, TextButton, TextField, icons, border_radius, alignment, border, colors, padding)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board import Board
from src.item import Item
from src.data_store import DataStore
import itertools

from custom.tamanos import Tamanos
from custom.textos import Textos
from custom.colores import Colores
from custom.iconos import Iconos

class BoardList(UserControl):
    id_counter = itertools.count()

    def __init__(self, board: "Board", store: DataStore, title: str, color: str = ""):
        super().__init__()
        self.board_list_id = next(BoardList.id_counter)
        self.store: DataStore = store
        self.board = board
        self.title = title
        self.color = color
        self.items = Column([], tight=True, spacing=4)
        self.items.controls = self.store.get_items(self.board_list_id)

    def build(self):

        self.new_item_field = TextField(
            label=Textos.tarjeta_nueva_nombre, 
            height=Tamanos.tarjeta_nueva_altura, 
            bgcolor=Colores.barra_agregar_actividad, 
            on_submit=self.add_item_handler)
        
        self.end_indicator = Container(
            bgcolor=Colores.indicador_movimiento,
            border_radius=border_radius.all(Tamanos.contenedor_footer_radioborde),
            height=Tamanos.contenedor_footer_altura,
            width=Tamanos.contenedor_footer_ancho,
            opacity=Tamanos.contenedor_footer_opacidad)
        
        self.edit_field = Row([
            TextField(value=self.title, 
                      width=Tamanos.btn_guardar_tarjeta_ancho, 
                      height=Tamanos.btn_guardar_tarjeta_altura,
                      content_padding=padding.only(left=Tamanos.btn_guardar_tarjeta_padding_L, 
                                                   bottom=Tamanos.btn_guardar_tarjeta_padding_R)),
            TextButton(text=Textos.btn_guardar_tarjeta, 
                       on_click=self.save_title)])
        
        self.header = Row(
            controls=[Text(value=self.title, style="titleMedium",text_align="left", overflow="clip", expand=True),
                      Container(
                          PopupMenuButton(
                              items=[PopupMenuItem(content=Text(value=Textos.pop_menu_editar, style="labelMedium",text_align="center", color=self.color),on_click=self.edit_title),
                                     PopupMenuItem(),
                                     PopupMenuItem(content=Text(value=Textos.pop_menu_eliminar, style="labelMedium",text_align="center", color=self.color),on_click=self.delete_list),
                                     PopupMenuItem(),
                                     PopupMenuItem(content=Text(value=Textos.pop_menu_mover, style="labelMedium",text_align="center", color=self.color))]),padding=padding.only(right=-10))],
                                     alignment="spaceBetween")
        
        self.inner_list = Container(
            content=Column([self.header,self.new_item_field,TextButton(content=Row([Icon(Iconos.agregar_tarjeta), Text(Textos.agregar_tarjeta, color=colors.BLACK38)], tight=True),on_click=self.add_item_handler),self.items,self.end_indicator], spacing=4,tight=True, data=self.title),
            width=Tamanos.tarjeta_ancho,
            border=border.all(Tamanos.tarjeta_borde,Colores.tarjeta_borde),
            border_radius=border_radius.all(Tamanos.tarjeta_borderadio),
            bgcolor=self.color if (self.color != "") else Colores.tarjeta_default_fondo,
            padding=padding.only(bottom=Tamanos.tarjeta_padding_B, 
                                 right=Tamanos.tarjeta_padding_R, 
                                 left=Tamanos.tarjeta_padding_L, 
                                 top=Tamanos.tarjeta_padding_T))
        
        self.view = DragTarget(
            group="items",
            content=Draggable(group="lists",content=DragTarget(group="lists",content=self.inner_list,data=self,on_accept=self.list_drag_accept,on_will_accept=self.list_will_drag_accept,on_leave=self.list_drag_leave)),
            data=self,
            on_accept=self.item_drag_accept,
            on_will_accept=self.item_will_drag_accept,
            on_leave=self.item_drag_leave)

        return self.view

    def item_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        self.add_item(src.data.item_text)
        src.data.list.remove_item(src.data)
        self.end_indicator.opacity = 0.0
        self.update()

    def item_will_drag_accept(self, e):
        if e.data == "true":
            self.end_indicator.opacity = 1.0
        self.update()

    def item_drag_leave(self, e):
        self.end_indicator.opacity = 0.0
        self.update()

    def list_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        l = self.board.board_lists
        to_index = l.index(e.control.data)
        from_index = l.index(src.content.data)
        l[to_index], l[from_index] = l[from_index], l[to_index]
        self.inner_list.border = border.all(2, Colores.tarjeta_borde)
        self.board.update()
        self.update()

    def list_will_drag_accept(self, e):
        if e.data == "true":
            self.inner_list.border = border.all(Tamanos.tarjeta_borde, 
                                                Colores.tarjeta_borde_hoover)
        self.update()

    def list_drag_leave(self, e):
        self.inner_list.border = border.all(Tamanos.tarjeta_borde, 
                                            Colores.tarjeta_borde)
        self.update()

    def delete_list(self, e):
        self.board.remove_list(self, e)

    def edit_title(self, e):
        self.header.controls[0] = self.edit_field
        self.header.controls[1].visible = False
        self.update()

    def save_title(self, e):
        self.title = self.edit_field.controls[0].value
        self.header.controls[0] = Text(value=self.title, style="titleMedium",
                                       text_align="left", overflow="clip", expand=True)

        self.header.controls[1].visible = True
        self.update()

    def add_item_handler(self, e):
        if self.new_item_field.value == "":
            return
        self.add_item()

    def add_item(self, item: str = None, chosen_control: Draggable = None, swap_control: Draggable = None):

        controls_list = [x.controls[1] for x in self.items.controls]
        to_index = controls_list.index(swap_control) if swap_control in controls_list else None
        from_index = controls_list.index(chosen_control) if chosen_control in controls_list else None
        control_to_add = Column([Container(bgcolor=Colores.item_fondo,
                                           border_radius=border_radius.all(Tamanos.item_borde),
                                           height=Tamanos.item_altura,
                                           alignment=alignment.center_right,
                                           width=Tamanos.item_ancho,
                                           opacity=Tamanos.item_opacidad)])
        
        # DRAG-N-DROP: misma_lista MOVER
        if ((from_index is not None) and (to_index is not None)):
            self.items.controls.insert(
                to_index, self.items.controls.pop(from_index))
            self.set_indicator_opacity(swap_control, 0.0)

        
        # DRAG-N-DROP: lista_distinta MOVER_MEDIO
        elif (to_index is not None):
            new_item = Item(self, self.store, item)
            control_to_add.controls.append(new_item)
            self.items.controls.insert(to_index, control_to_add)

        # DRAG-N-DROP: lista_distinta AGREGAR_FONDO
        else:
            new_item = Item(self, self.store, item) if item else Item(
                self, self.store, self.new_item_field.value)
            control_to_add.controls.append(new_item)
            self.items.controls.append(control_to_add)
            self.store.add_item(self.board_list_id, new_item)
            self.new_item_field.value = ""

        self.view.update()
        self.page.update()

    def remove_item(self, item: Item):
        controls_list = [x.controls[1] for x in self.items.controls]
        del self.items.controls[controls_list.index(item)]
        self.store.remove_item(self.board_list_id, item.item_id)
        self.view.update()

    def set_indicator_opacity(self, item, opacity):
        controls_list = [x.controls[1] for x in self.items.controls]
        self.items.controls[controls_list.index(item)].controls[0].opacity = opacity
        self.view.update()
