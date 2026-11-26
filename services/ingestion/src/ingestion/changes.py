"""Detect what changed between two states of the same match."""

from dataclasses import dataclass

from ingestion.state import GameStatus, MatchState, MatchStatus


@dataclass(frozen=True)
class MatchStatusChanged:
    match_id: int
    old: MatchStatus | None
    new: MatchStatus


@dataclass(frozen=True)
class GameStatusChanged:
    match_id: int
    position: int
    old: GameStatus | None
    new: GameStatus
    winner_id: int | None


@dataclass(frozen=True)
class ScoreChanged:
    match_id: int
    team_id: int
    old: int | None
    new: int


type Change = MatchStatusChanged | GameStatusChanged | ScoreChanged


def detect_changes(old: MatchState | None, new: MatchState) -> list[Change]:
    """Return the changes from `old` to `new`.

    `old` is None when the match has never been seen before.
    """
    if old is not None and old.match_id != new.match_id:
        raise ValueError(f"cannot compare match {old.match_id} with match {new.match_id}")

    if old == new:
        return []

    changes: list[Change] = []
    match_id = new.match_id

    old_status = old.status if old else None
    if old_status != new.status:
        changes.append(MatchStatusChanged(match_id, old_status, new.status))

    old_games = {g.position: g for g in old.games} if old else {}
    for game in new.games:
        previous = old_games.get(game.position)
        previous_status = previous.status if previous else None
        if previous_status != game.status:
            changes.append(
                GameStatusChanged(match_id, game.position, previous_status, game.status, game.winner_id)
            )

    old_scores = {s.team_id: s.score for s in old.scores} if old else {}
    for score in new.scores:
        previous_score = old_scores.get(score.team_id)
        if previous_score != score.score:
            changes.append(ScoreChanged(match_id, score.team_id, previous_score, score.score))

    return changes
