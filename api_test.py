from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

email = "api_test4@example.com"
password = "foobar"

print("registering")
r = client.post("/auth/register", json={"email": email, "password": password, "name": "T"})
print(r.status_code, r.text)

print("logging in")
r = client.post("/auth/login", json={"email": email, "password": password})
print(r.status_code, r.text)

if r.status_code == 200:
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("trying /transactions")
r2 = client.get("/transactions", headers=headers)
print(r2.status_code, r2.text)
