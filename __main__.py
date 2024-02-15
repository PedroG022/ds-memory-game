import logging

import flet as ft
from fletrt import Router

import src.scrapper as scrapper
from src.pages import GamePage, HostPage, JoinPage, HomePage

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | [%(name)s] %(message)s",
)

# Ignore INFO and DEBUG logs from the flet packages
logging.getLogger('flet_core').setLevel(logging.ERROR)
logging.getLogger('flet_runtime').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


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


if __name__ == "__main__":
    scrapper.run(lambda: ft.app(target=main))
