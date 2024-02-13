import logging
import pickle
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Event

from src.infra.entities import Identifier, Message

logger = logging.getLogger(__name__)


class Server:

    # Server's parameters initialization
    def __init__(self, port: int):
        self.__socket: socket = socket(AF_INET, SOCK_STREAM)

        self.__port = port

        self.__server_shutdown: Event = Event()
        self.__client_sockets: dict[Identifier: socket] = {}

    # Method to start the server
    def start(self):
        self.__socket.bind(('127.0.0.1', self.__port))
        self.__socket.listen()

        thread_listen_clients = Thread(target=self.__listen_clients)
        thread_listen_clients.start()

        logger.info(f'Server started successfully at \'localhost:{self.__port}\', waiting for connections...')

    # Method to stop the server
    def stop(self):
        logger.info('Shutting down server...')

        self.__disconnect_all_clients()
        self.__server_shutdown.set()
        self.__socket.close()

    # Method that runs once a new client is connected
    def __on_new_client(self, client_socket: socket):
        identifier_str: str = pickle.loads(client_socket.recv(1024))
        identifier: Identifier = Identifier(identifier_str)

        identifier_dump: bytes = pickle.dumps(identifier)
        client_socket.sendall(identifier_dump)

        logger.info(f'New client {client_socket.getsockname()}: "{identifier.name}"')

        self.on_new_client(identifier)

        self.__client_sockets[identifier] = client_socket
        self.__handle_client_messages(client_socket, identifier)

    def __disconnect_all_clients(self):
        for client_socket in self.__client_sockets.values():
            client_socket: socket
            client_socket.close()

    # Handles the messages that will be received from the clients
    def __handle_client_messages(self, client_socket: socket, client_identifier: Identifier):
        while not self.__server_shutdown.is_set():
            try:
                data = client_socket.recv(1024)
                message: Message = pickle.loads(data)

                # Sets the message identifier for the sender
                message.identifier = client_identifier

                # Set the message received date
                message.date = datetime.now()

                self.on_message_received(message)
            # Catches clients disconnections and other errors
            except Exception as exception:
                if isinstance(exception, ConnectionResetError):
                    del self.__client_sockets[client_identifier]
                    self.on_client_disconnect(client_identifier)
                elif not isinstance(exception, ConnectionAbortedError):
                    logger.error(f'Error while handling client message: {exception}')
                break

    # Broadcasts a message to all clients
    def broadcast(self, message: Message):
        for identifier in self.__client_sockets.keys():
            identifier: Identifier

            # Verifies if the message sender is the target, if it is, then it's ignored
            if not message.identifier == identifier:
                client_socket: socket = self.__client_sockets[identifier]
                message_dump = pickle.dumps(message)
                client_socket.sendall(message_dump)

    # Method to handle new client connections
    def __listen_clients(self):
        while not self.__server_shutdown.is_set():
            try:
                client_socket, address = self.__socket.accept()

                handle_client_thread: Thread = Thread(target=self.__on_new_client, args=(client_socket,))
                handle_client_thread.start()
            except Exception as exception:
                # Accept method was aborted by socket's disconnection,
                # so we can ignore this
                if not (isinstance(exception, OSError) and exception.errno == 10038):
                    logger.warning(f'Error while listening for clients {exception}')

        logger.info('Server stopped.')

    # Event handlers
    # ===================

    def on_new_client(self, identifier: Identifier):
        pass

    def on_client_disconnect(self, identifier: Identifier):
        pass

    def on_message_received(self, message: Message):
        pass
