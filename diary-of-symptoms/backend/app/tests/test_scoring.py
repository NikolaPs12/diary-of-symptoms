from app.services.scoring import determine_health_trend


def test_health_trend_is_stable_with_no_scores():
    assert determine_health_trend([]) == "stable"


def test_health_trend_is_improving():
    assert determine_health_trend([60, 65, 72]) == "improving"


def test_health_trend_is_declining():
    assert determine_health_trend([80, 75, 70]) == "declining"


def test_health_trend_is_stable_with_small_change():
    assert determine_health_trend([80, 82, 84]) == "stable"