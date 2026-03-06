import sys
sys.path.insert(0, '.')

from routers.menu import router
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

client = TestClient(app)
response = client.get("/api/menus?lang=zh-CN")
print("Status:", response.status_code)
print("Response:", response.json()[:2] if isinstance(response.json(), list) else response.json())
