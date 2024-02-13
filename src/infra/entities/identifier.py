import uuid


class Identifier:
    def __init__(self, name: str):
        self.id: uuid = uuid.uuid4()
        self.name: str = name
