import json
from pathlib import Path

import pytest

from ingestion.changes import (
    GameStatusChanged,
    MatchStatusChanged,
    ScoreChanged,
    detect_changes,
)
from ingestion.state import GameStatus, MatchState, MatchStatus

FIXTURES = Path(__file__).parent / "fixtures" / "sample"


def load_match(fixture: str, match_id: int) -> MatchState:
    matches = json.loads((FIXTURES / fixture).read_text())
    raw = next(m for m in matches if m["id"] == match_id)
    return MatchState.from_api(raw)


def test_same_state_has_no_changes():
    state = load_match("running.json", 1829555)

    assert detect_changes(state, state) == []


def test_match_going_live():
    # TME vs ELL: not started in upcoming.json, map 1 won in running-2.json
    old = load_match("upcoming.json", 1828509)
    new = load_match("running-2.json", 1828509)

    assert detect_changes(old, new) == [
        MatchStatusChanged(1828509, MatchStatus.NOT_STARTED, MatchStatus.RUNNING),
        GameStatusChanged(1828509, 1, GameStatus.NOT_STARTED, GameStatus.FINISHED, 139647),
        GameStatusChanged(1828509, 2, GameStatus.NOT_STARTED, GameStatus.RUNNING, None),
        ScoreChanged(1828509, 139647, 0, 1),
    ]


def test_first_time_seen_reports_everything():
    new = load_match("running.json", 1829555)

    changes = detect_changes(None, new)

    assert changes[0] == MatchStatusChanged(1829555, None, MatchStatus.RUNNING)
    assert len(changes) == 1 + len(new.games) + len(new.scores)


def test_comparing_different_matches_fails():
    a = load_match("running.json", 1829555)
    b = load_match("running.json", 1831482)

    with pytest.raises(ValueError):
        detect_changes(a, b)
