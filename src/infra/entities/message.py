from datetime import datetime
from typing import Optional

from src.infra.entities import Identifier


class Message:
    def __init__(self, body: any, identifier: Identifier = None):
        self.body: any = body
        self.identifier: Identifier = identifier

        self.date: Optional[datetime] = None
