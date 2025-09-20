import os, json, pytest
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

def load(f):
    with open(f,"r") as fp: return json.load(fp)
