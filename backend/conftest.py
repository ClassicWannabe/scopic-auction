import pytest

from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Helper object for HTTP requests"""
    return APIClient()
