from fastapi.testclient import TestClient
from explorer.web import app


client = TestClient(app)


def test_random_dialog():
    response = client.get("/curiosity/dialog/random")
    assert response.status_code == 200


def test_single_dialog():
    response = client.get("/curiosity/dialog/1215")
    assert response.status_code == 200


def test_dialogs_by_topic():
    response = client.get("/curiosity/dialog/topic/Africa")
    assert response.status_code == 200


def test_dialogs_api():
    response = client.get("/curiosity/dialogs")
    assert response.status_code == 200
    parsed = response.json()
    assert len(parsed["dialogs"]) != 0
    assert parsed["n_dialogs"] != 0
    assert parsed["n_pages"] != 0
    assert parsed["page"] == 1
    assert parsed["topic"] is None


def test_topics_api():
    response = client.get("/curiosity/topics")
    assert response.status_code == 200
    parsed = response.json()
    assert len(parsed["topics"]) != 0
    assert isinstance(parsed["topics"][0], str)
