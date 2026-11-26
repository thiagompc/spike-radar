"""Relevant match state, used to detect changes."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self


class MatchStatus(StrEnum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    FINISHED = "finished"
    CANCELED = "canceled"
    POSTPONED = "postponed"


class GameStatus(StrEnum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    FINISHED = "finished"
    NOT_PLAYED = "not_played"


class UnknownPayloadError(ValueError):
    """The API payload has a shape or a value we don't recognize."""


@dataclass(frozen=True)
class TeamScore:
    team_id: int
    score: int


@dataclass(frozen=True)
class GameState:
    position: int
    status: GameStatus
    winner_id: int | None


@dataclass(frozen=True)
class MatchState:
    match_id: int
    status: MatchStatus
    scores: tuple[TeamScore, ...]
    games: tuple[GameState, ...]

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Self:
        """Convert a raw PandaScore API match into a MatchState."""
        try:
            scores = tuple(
                sorted(
                    (TeamScore(team_id=r["team_id"], score=r["score"]) for r in raw["results"]),
                    key=lambda s: s.team_id,
                )
            )
            games = tuple(
                sorted(
                    (
                        GameState(
                            position=g["position"],
                            status=GameStatus(g["status"]),
                            winner_id=g["winner"]["id"] if g["winner"] else None,
                        )
                        for g in raw["games"]
                    ),
                    key=lambda g: g.position,
                )
            )
            return cls(
                match_id=raw["id"],
                status=MatchStatus(raw["status"]),
                scores=scores,
                games=games,
            )
        except (KeyError, TypeError, ValueError) as e:
            raise UnknownPayloadError(f"match {raw.get('id')!r}: {e!r}") from e
