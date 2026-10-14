"""Automated checks for plantnet.py: turning Pl@ntNet's reply into what the page needs."""

from plantnet import summarise, to_percent


def make_reply(*results):
    """Build a Pl@ntNet-style reply from (score, scientific name, common names) tuples."""
    return {"results": [
        {"score": score, "species": {"scientificNameWithoutAuthor": name, "commonNames": common}}
        for score, name, common in results
    ]}


# --- Scores become whole percentages (SPEC.md acceptance criterion 4) ---

def test_score_becomes_whole_percent():
    assert to_percent(0.92613) == 92


def test_percent_always_rounds_down():
    assert to_percent(0.4999) == 49


def test_percent_ignores_tiny_computer_maths_errors():
    # 0.29 * 100 is 28.999999999999996 inside a computer.
    assert to_percent(0.29) == 29


# --- The 50% rule (SPEC.md story 6: 49% warns, 50% doesn't) ---

def test_49_percent_is_not_confident():
    assert summarise(make_reply((0.49, "Bellis perennis", ["Common daisy"])))["confident"] is False


def test_50_percent_is_confident():
    assert summarise(make_reply((0.50, "Bellis perennis", ["Common daisy"])))["confident"] is True


def test_just_under_50_percent_is_not_confident():
    # Would show as "49%", so it must get the warning.
    assert summarise(make_reply((0.4999, "Bellis perennis", ["Common daisy"])))["confident"] is False


# --- Names ---

def test_first_common_name_is_used():
    summary = summarise(make_reply((0.9, "Bellis perennis", ["Common daisy", "Lawn daisy"])))
    assert summary["candidates"][0]["common_name"] == "Common daisy"


def test_missing_common_name_becomes_none():
    summary = summarise(make_reply((0.9, "Rare plant", [])))
    assert summary["candidates"][0]["common_name"] is None


# --- Number of candidates ---

def test_keeps_at_most_3_candidates():
    reply = make_reply(*[(0.1, f"Plant {n}", []) for n in range(5)])
    assert len(summarise(reply)["candidates"]) == 3


def test_fewer_than_3_candidates_is_fine():
    summary = summarise(make_reply((0.3, "Rosa canina", ["Dog rose"])))
    assert len(summary["candidates"]) == 1
