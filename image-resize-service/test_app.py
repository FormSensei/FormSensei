#
# RUN TEST WITH: pytest test_app.py
#

from app import app
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_resize_image():
    with open("AFK.png", "rb") as image_file:
        response = client.post(
            "/resize/",
            files={"file": ("test_image.png", image_file, "image/png")},
            data={"width": 50, "height": 50}
        )
    assert response.status_code == 200
    assert response.json()["filename"] == "AFK.png"
    assert response.json()["content"] is not None

if __name__ == "__main__":
    pytest.main()