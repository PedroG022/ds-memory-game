import flet as ft
from flet_core import View, Control
from fletrt import Route


class HostPage(Route):
    def connect(self, port: str):
        port = int(port)

        self.page.session.set('port', port)
        self.page.session.set('mode', 'server')

        self.go('/game')

    def body(self) -> Control:
        field = ft.TextField(label='Port', value='37001')
        connect = ft.ElevatedButton('Host', height=50, expand=True, on_click=lambda _: self.connect(field.value))

        col = ft.Column([
            field,
            ft.Row([connect])
        ])

        return col

    def view(self) -> View:
        base = super().view()

        base.padding = 16
        base.vertical_alignment = ft.MainAxisAlignment.CENTER
        base.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        return base
