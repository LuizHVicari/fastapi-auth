from dataclasses import dataclass


@dataclass(frozen=True)
class LoginChallenge:
    challenge: str
    subject: str | None
    skip: bool
    requested_scope: list[str]
    client_id: str


@dataclass(frozen=True)
class ConsentChallenge:
    challenge: str
    subject: str
    skip: bool
    requested_scope: list[str]
    client_id: str


@dataclass(frozen=True)
class LogoutChallenge:
    challenge: str
    subject: str | None
    sid: str | None
