from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_prediction_endpoint():
    payload = {
        "boxes": [
            [20, 30, 250, 60],
            [20, 100, 320, 45],
            [20, 160, 420, 300]
        ]
    }
    response = client.post("/api/v1/predict", json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
if __name__ == "__main__":
    test_prediction_endpoint()