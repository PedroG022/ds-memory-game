import os
import random
import time
from os import path
from threading import Thread
from typing import Optional, Union

import flet as ft
from fletrt import Route

from src.entities import GameMessage, Points
from src.enums import Status, Subject
from src.infra import Server, Client, Identifier

POINTS_PER_CARD = 100

UNIQUE_COUNT = 10
CARDS_COUNT = UNIQUE_COUNT * 2

CARD_SIZE = 100
RUNS = 4
GRID_SIZE = 500

IMAGES_PATH = './out/'


def get_pairs_list_shuffled():
    files = os.listdir(IMAGES_PATH)
    pngs = [file for file in files if file[-4:] == '.png']

    selected = []

    for i in range(UNIQUE_COUNT):
        current = random.choice(pngs)
        current = pngs.pop(pngs.index(current))
        selected.append(current)

    selected_pairs = selected * 2
    random.shuffle(selected_pairs)

    return selected_pairs


class GamePage(Route):
    def __init__(self):
        super().__init__()

        self.client_identifier = None
        self.open_cards = []

        self.turn = False
        self.last = None

        self.found_cards = 0
        self.found_cards_list = []

        self.points: Points = Points()
        self.points.client_points = 0
        self.points.server_points = 0

        self.grid: Optional[ft.GridView] = None
        self.info_text: Optional[ft.Text] = None
        self.points_text: Optional[ft.Text] = None

    def click_card(self,
                   event: Union[ft.ContainerTapEvent, ft.Container],
                   connection: Union[Client, Server],
                   broadcast: bool,
                   by_server: bool):

        is_server = isinstance(connection, Server)

        control: ft.Container = event.control if isinstance(event, ft.ContainerTapEvent) else event

        image_name = control.data

        self.last = image_name
        image_path = path.join(IMAGES_PATH, image_name)

        image = ft.Image(src=image_path)
        control.content = image
        control.disabled = True

        self.page.update()

        message: GameMessage = GameMessage(subject=Subject.ROUND, body=self.grid.controls.index(control), count=0)

        if broadcast:
            if is_server:
                connection.send_message(self.client_identifier, message)
            else:
                connection.send_message(message)

        self.open_cards.append(control)

        server_ref = None
        client_ref = None

        if is_server:
            server_ref = connection
        else:
            client_ref = connection

        if len(self.open_cards) == 2:
            self.all_cards_status(Status.DISABLED)
            Thread(target=self.check_match, args=(by_server, is_server, server_ref, client_ref)).start()

    def cs(self, status: Status, found: bool):
        not_found_cards = [card for card in self.grid.controls if card not in self.found_cards_list]

        if found:
            not_found_cards = [card for card in self.grid.controls if card not in not_found_cards]

        for card in not_found_cards:
            card.disabled = status.value

        self.page.update()

    def check_match(self, played_by_server: bool, executed_by_server: bool, server: Optional[Server] = None,
                    client: Optional[Client] = None):
        card1, card2 = self.open_cards

        match = False

        if card1.data == card2.data:
            match = True
            card1.onclick = None
            card2.onclick = None

            self.found_cards_list.extend([card1, card2])

            if executed_by_server and server:
                self.found_cards += 2

            if played_by_server:
                card1.bgcolor = ft.colors.GREEN
                card2.bgcolor = ft.colors.GREEN

                if executed_by_server:
                    self.points.server_points += POINTS_PER_CARD
            else:
                card1.bgcolor = ft.colors.BLUE
                card2.bgcolor = ft.colors.BLUE

                if executed_by_server and server:
                    self.points.client_points += POINTS_PER_CARD

            if executed_by_server and server:
                server.send_message(self.client_identifier, GameMessage(Subject.POINTS, 0, self.points))
                self.points_text.value = f'Server: {self.points.server_points}\tClient: {self.points.client_points}'

        time.sleep(2)

        card1.content = ft.Container()
        card2.content = ft.Container()

        self.open_cards.clear()
        self.page.update()

        done_message: GameMessage = GameMessage(Subject.TURN, 0, 0)

        if executed_by_server and server:
            winner = self.check_endgame()

            if winner != -1:
                server.send_message(self.client_identifier, GameMessage(Subject.END_GAME, 0, winner))
                self.declare_winner(winner, True)

        if played_by_server and executed_by_server and server:
            if not match:
                server.send_message(self.client_identifier, done_message)
            else:
                self.cs(Status.ENABLED, False)
        elif client and not played_by_server:
            if not match:
                client.send_message(done_message)
            else:
                self.cs(Status.ENABLED, False)

        self.page.update()

    def set_colors(self, color: ft.colors):
        for control in self.grid.controls:
            control.bgcolor = color

        self.page.update()

    def declare_winner(self, winner: int, server: bool):
        if winner == 0:
            self.points_text.value = 'Server wins'

            if server:
                self.set_colors(ft.colors.GREEN)
            else:
                self.set_colors(ft.colors.RED)
        elif winner == 1:
            self.points_text.value = 'Client wins'

            if server:
                self.set_colors(ft.colors.RED)
            else:
                self.set_colors(ft.colors.GREEN)
        elif winner == 2:
            self.points_text.value = 'Draw'

            self.set_colors(ft.colors.TEAL)
        else:
            self.points_text.value = '???'
            self.set_colors(ft.colors.ORANGE)

        self.page.update()

    def check_endgame(self) -> int:
        if self.found_cards == CARDS_COUNT:

            if self.points.server_points > self.points.client_points:
                return 0
            elif self.points.server_points < self.points.client_points:
                return 1
            else:
                return 2

        return -1

    def initialize_cards(self, connection: Union[Server, Client], card_list: list):
        by_server: bool = isinstance(connection, Server)

        for i in range(CARDS_COUNT):
            self.grid.controls[i].data = card_list[i]

        for i in range(CARDS_COUNT):
            self.grid.controls[i].on_click = \
                lambda event: self.click_card(event, connection, broadcast=True, by_server=by_server)

        self.page.update()

    def all_cards_status(self, status: Status):
        for control in self.grid.controls:
            control.disabled = status.value

        self.page.update()

    def on_disconnect(self):
        self.info_text.value = 'Disconnected!'

        self.all_cards_status(Status.DISABLED)
        self.set_colors(ft.colors.GREY)

        self.page.update()

    def server(self):
        server = Server(self.page.session.get('port'))

        def on_conn(identifier: Identifier):
            if server.client_count() > 1:
                server.disconnect_client(identifier)
                return

            self.info_text.value = f'Connected with {identifier.name}'
            self.page.title = f'Game with {identifier.name}'

            self.page.update(self.info_text)

            self.set_colors(ft.colors.PURPLE_400)

            self.client_identifier = identifier

            card_list = get_pairs_list_shuffled()
            self.initialize_cards(server, card_list)

            server.send_message(identifier, GameMessage(subject=Subject.MAP, count=0, body=card_list))
            self.all_cards_status(Status.DISABLED)

        def on_msg(message: GameMessage):
            if message.subject == Subject.ROUND:
                target_card = self.grid.controls[message.body]

                self.click_card(target_card, server, broadcast=False, by_server=False)

                if len(self.open_cards) == 2:
                    Thread(target=self.check_match, args=(False, True)).start()

            if message.subject == Subject.TURN:
                self.info_text.value = 'Your turn'
                self.page.update()

                self.cs(Status.ENABLED, False)

        server.on_new_client = on_conn
        server.on_message_received = on_msg
        server.on_client_disconnect = lambda _: self.on_disconnect()

        server.start()

    def client(self):
        client = Client(self.page.session.get('host'), self.page.session.get('port'), self.page.session.get('username'))

        def on_message(message: GameMessage):
            if message.subject == Subject.MAP:
                card_list = message.body

                self.initialize_cards(client, card_list)
                self.page.update()

            if message.subject == Subject.ROUND:
                self.click_card(self.grid.controls[message.body], client, broadcast=False, by_server=True)

                if len(self.open_cards) == 2:
                    Thread(target=self.check_match, args=(True, False, None, client)).start()

            if message.subject == Subject.POINTS:
                points: Points = message.body
                self.points = points
                self.points_text.value = f'Server: {points.server_points}\tClient: {points.client_points}'

            if message.subject == Subject.END_GAME:
                self.declare_winner(message.body, False)

            if message.subject == Subject.TURN:
                self.info_text.value = 'Your turn'
                self.page.update()

                self.cs(Status.ENABLED, False)

        client.on_message = on_message
        client.on_disconnect = self.on_disconnect
        client.connect()

    def body(self):
        get_pairs_list_shuffled()
        server = self.page.session.get('mode') == 'server'

        self.info_text = ft.Text()
        self.points_text = ft.Text()

        if server:
            Thread(target=self.server).start()
        else:
            Thread(target=self.client).start()

        color = ft.colors.GREY if server else ft.colors.PURPLE_400

        self.grid = ft.GridView(
            height=GRID_SIZE,
            width=GRID_SIZE,
            max_extent=CARD_SIZE,
            runs_count=RUNS,
        )

        for i in range(CARDS_COUNT):
            container = ft.Container(
                bgcolor=color,
            )

            self.grid.controls.append(container)

        return ft.Column(
            [
                self.info_text,
                self.points_text,
                self.grid
            ]
        )

    def view(self):
        base = super().view()

        base.vertical_alignment = ft.MainAxisAlignment.CENTER
        base.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        return base
