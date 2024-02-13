import flet as ft
from flet_core import View, Control
from fletrt import Route

from src.infra import Server, Client, Identifier, Message


class GamePage(Route):

    def server(self):
        server = Server(self.page.session.get('port'))

        connected = False

        def on_conn(identifier: Identifier):
            pass

        def on_msg(message: Message):
            pass

        def on_dsc(identifier: Identifier):
            pass

        server.on_new_client = on_conn
        server.on_message_received = on_msg
        server.on_client_disconnect = on_dsc

        server.start()

    def client(self):
        client = Client(self.page.session.get('host'), self.page.session.get('port'))
        client.connect()

        print('Connected to server')

    def body(self) -> Control:
        server = self.page.session.get('mode') == 'server'

        if server:
            self.server()
        else:
            self.client()

        return ft.Text()

    def view(self) -> View:
        base = super().view()

        base.vertical_alignment = ft.MainAxisAlignment.CENTER
        base.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        return base
