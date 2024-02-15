from src.enums import Subject
from src.infra import Message


class GameMessage(Message):
    def __init__(self, subject: Subject, count: int, body: any):
        super().__init__(body)

        self.subject = subject
        self.count = count
