from dataclasses import dataclass


@dataclass(frozen=True)
class FlowUI:
    action: str
    hidden_fields: list[dict[str, str]]
    error: str | None
