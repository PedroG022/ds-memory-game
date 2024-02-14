import logging
import pickle
import threading
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable, Optional

from random_username.generate import generate_username

from src.infra.entities import Identifier, Message

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, host: str, port: int, identifier: str = None):
        self.connection: socket = socket(AF_INET, SOCK_STREAM)

        self.host: str = host
        self.port: int = port

        if not identifier:
            logger.info('Client identifier is not present. Generating a random one...')
            identifier = generate_username()[0]

        self.identifier: str = identifier

        self.on_message: Optional[Callable[[Message], None]] = None

    def __handle_io(self):
        while self.connection:
            data = self.connection.recv(1024)
            message: Message = pickle.loads(data)

            if self.on_message:
                self.on_message(message)

    # Method to set the handler for the messages received from the server
    def set_on_message_handler(self, handler: Callable[[Message], None]):
        self.on_message = handler

    # Method to send messages to the server
    def send_message(self, message: Message):
        if self.connection:
            message_dump = pickle.dumps(message)
            self.connection.send(message_dump)

    # Method used to establish a connection to the server
    def connect(self):
        try:
            self.connection.connect((self.host, self.port))
            logging.info('Connection established!')

            # Identification handling
            # Dump the client identifier string and send it to the server
            identifier_dump = pickle.dumps(self.identifier)
            self.connection.sendall(identifier_dump)

            # Receive the ClientIdentifier object from the server
            client_identifier: Identifier = pickle.loads(self.connection.recv(1024))
            logging.info(f'Received identifier: {client_identifier.id}')

            io_thread = threading.Thread(target=self.__handle_io)
            io_thread.start()

            return client_identifier
        except ConnectionRefusedError as error:
            logging.error('Connection refused!')
            raise ConnectionRefusedError from error
        except ConnectionError as error:
            logging.error('Connection error!')
            raise ConnectionError from error

    # Disconnects from the server
    def disconnect(self):
        self.connection.close()
