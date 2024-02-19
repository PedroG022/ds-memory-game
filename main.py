import argparse
import logging

import flet as ft
from fletrt import Router

import src.scrapper as scrapper
from src.pages import GamePage, HostPage, JoinPage, HomePage

parser = argparse.ArgumentParser()

parser.add_argument('--web', action='store_true', help='Run the game in web mode.')

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | [%(name)s] %(message)s",
)

# Ignore INFO and DEBUG logs from the flet packages
logging.getLogger('flet_core').setLevel(logging.ERROR)
logging.getLogger('flet_runtime').setLevel(logging.ERROR)
logging.getLogger('flet').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


def configure_page(page: ft.Page):
    page.window_width = 640
    page.window_height = 580

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
    web_args = {}

    if args.web:
        web_args = {
            'port': 40444,
            'view': ft.WEB_BROWSER,
            'assets_dir': './'
        }

    scrapper.run(lambda: ft.app(target=main, **web_args))
