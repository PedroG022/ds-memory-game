import logging
import pickle
import threading
import time
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
        self.__client_disconnection_events: dict[Identifier: Event] = {}

    def client_count(self) -> int:
        return len(self.__client_sockets)

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

    # Disconnects all the connected clients
    def __disconnect_all_clients(self):
        for identifier in self.__client_sockets.keys():
            self.disconnect_client(identifier)

    # Disconnects a client from the server given its identifier
    def disconnect_client(self, identifier: Identifier):
        logger.info(f'Received disconnection request for client {identifier}')

        if identifier in self.__client_disconnection_events.keys():
            event: Event = self.__client_disconnection_events[identifier]
            event.set()
        else:
            logger.error(f'Unable to find client {identifier} for disconnection request!')

    # Listen events to disconnect clients from the server
    def __disconnect_listener(self, client_socket: socket, identifier: Identifier, event: Event):
        while not event.is_set():
            time.sleep(0.1)

        logger.info(f'Disconnection event triggered for client {identifier}')

        client_socket.close()

        del self.__client_sockets[identifier]
        del self.__client_disconnection_events[identifier]

        self.on_client_disconnect(identifier)

    # Handles the messages that will be received from the clients
    def __handle_client_messages(self, client_socket: socket, identifier: Identifier):
        while not self.__server_shutdown.is_set():
            try:
                data = client_socket.recv(1024)
                message: Message = pickle.loads(data)

                # Sets the message identifier for the sender
                message.identifier = identifier

                # Set the message received date
                message.date = datetime.now()

                self.on_message_received(message)
            # Catches clients disconnections and other errors
            except Exception as exception:
                if isinstance(exception, ConnectionResetError):
                    del self.__client_sockets[identifier]
                    del self.__client_disconnection_events[identifier]

                    self.on_client_disconnect(identifier)
                elif not isinstance(exception, ConnectionAbortedError):
                    logger.error(f'Error while handling client message: {exception}')
                break

    def send_message(self, target_client_identifier: Identifier, message: Message):
        if target_client_identifier not in self.__client_sockets:
            logger.error(f'Client not found while trying to send message: {target_client_identifier}')
            return

        encoded_message: bytes = pickle.dumps(message)
        client_socket: socket = self.__client_sockets[target_client_identifier]
        client_socket.send(encoded_message)

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
                # Accept the connection from the client
                client_socket, address = self.__socket.accept()

                # Receives the identifier
                identifier_str: str = pickle.loads(client_socket.recv(1024))
                identifier: Identifier = Identifier(identifier_str)

                # Sends the identifier back, with the UUID filled
                identifier_dump: bytes = pickle.dumps(identifier)
                client_socket.sendall(identifier_dump)

                # Logs the new connection
                logger.info(f'New client {client_socket.getsockname()}: "{identifier.name}"')

                # Add the client socket to the server's socket list
                self.__client_sockets[identifier] = client_socket

                # The event to handle disconnections from the server
                closure_event: Event = Event()
                self.__client_disconnection_events[identifier] = closure_event

                # Triggers the event handler
                new_client_thread = threading.Thread(target=self.on_new_client, args=(identifier,))
                new_client_thread.start()

                # Threads to handle messaging and disconnection events
                message_handler_thread: Thread = Thread(target=self.__handle_client_messages,
                                                        args=(client_socket, identifier))

                disconnection_handler_thread: Thread = Thread(target=self.__disconnect_listener,
                                                              args=(client_socket, identifier, closure_event))

                message_handler_thread.start()
                disconnection_handler_thread.start()
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
