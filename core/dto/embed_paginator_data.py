from dataclasses import dataclass


@dataclass(frozen=True)
class EmbedPaginatorData:
    title: str
    data: dict[str, list[str]]
    footer: str | None = None