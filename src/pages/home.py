import flet as ft
from flet_core import View, Control
from fletrt import Route


class HomePage(Route):

    def body(self) -> Control:
        col = ft.Column([
            ft.ElevatedButton('Join', width=200, height=50, on_click=lambda _: self.go('/join')),
            ft.ElevatedButton('Host', width=200, height=50, on_click=lambda _: self.go('/host')),
        ])

        return col

    def view(self) -> View:
        base = super().view()

        base.vertical_alignment = ft.MainAxisAlignment.CENTER
        base.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        return base
