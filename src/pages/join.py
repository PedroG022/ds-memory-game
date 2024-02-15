import flet as ft
from flet_core import View, Control
from fletrt import Route


class JoinPage(Route):
    def connect(self, address: str, username: str):
        address, port = address.split(':')

        self.page.session.set('username', username)
        self.page.session.set('host', address)
        self.page.session.set('port', int(port))
        self.page.session.set('mode', 'client')

        self.go('/game')

    def body(self) -> Control:
        name_field = ft.TextField(label='Username')
        field = ft.TextField(label='IP:Port', value='127.0.0.1:37001')
        connect = ft.ElevatedButton('Connect', height=50, expand=True,
                                    on_click=lambda _: self.connect(field.value, name_field.value))

        col = ft.Column([
            name_field,
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
