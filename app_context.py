from dataclasses import dataclass

from services.state import StateService


@dataclass(frozen=True)
class AppContext:
    state_service: StateService