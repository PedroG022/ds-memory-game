import flet as ft
from fletrt import Router

from src.pages import GamePage, HostPage, JoinPage, HomePage


def configure_page(page: ft.Page):
    page.window_width = 640
    page.window_height = 480

    page.window_maximizable = False
    page.window_resizable = False

    page.window_center()


def main(page: ft.Page):
    configure_page(page)

    router = Router(routes={
        '/': HomePage(),
        '/join': JoinPage(),
        '/host': HostPage(),
        '/game': GamePage()
    }, page=page)

    router.install()

    page.update()


ft.app(target=main)
