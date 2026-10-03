from typing import NamedTuple
from dataclasses import dataclass

from enums import MessengerType
from type_aliases import ServerUid


class MessengerRegistration(NamedTuple):
    messenger_type: MessengerType
    server_uid: ServerUid
    name: str