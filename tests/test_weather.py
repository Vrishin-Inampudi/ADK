from unittest.mock import MagicMock, patch

from weather_agent import agent as w

GEO = {"results": [{"latitude": 42.36, "longitude": -71.06, "timezone": "America/New_York",
                    "name": "Boston", "admin1": "Massachusetts", "country": "United States"}]}
FORECAST = {"current_weather": {"temperature": 10.0, "windspeed": 5.0, "weathercode": 1}}


def _resp(payload):
    m = MagicMock()
    m.json.return_value = payload
    return m


def test_get_weather():
    with patch.object(w.requests, "get", side_effect=[_resp(GEO), _resp(FORECAST)]):
        result = w.get_weather("Boston")
    assert result["status"] == "success"
    assert result["report"]["location"] == "Boston, Massachusetts, United States"
    assert result["report"]["temperature_c"] == 10.0


def test_get_current_time():
    with patch.object(w.requests, "get", return_value=_resp(GEO)):
        result = w.get_current_time("Boston")
    assert result["report"]["timezone"] == "America/New_York"


def test_unknown_city():
    with patch.object(w.requests, "get", return_value=_resp({})):
        assert w.get_weather("Nowhereville")["status"] == "error"
