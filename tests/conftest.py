
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.response_cache import response_cache


@pytest.fixture(autouse=True)
def clear_response_cache():
    response_cache.clear()
    yield
    response_cache.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
