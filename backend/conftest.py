import re
import os
from datetime import datetime
import pytest

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core import models


def sample_auction_item(**params):
    """Create and return `AuctionItem` object"""

    defaults = {
        "title": "title",
        "description": "description",
        "init_bid": 2.99,
        "bid_close_date": datetime.now(),
        "picture": SimpleUploadedFile("testfile.jpeg", b"file_content"),
    }
    defaults.update(**params)

    return models.AuctionItem.objects.create(**defaults)


def purge_files(dir: str, pattern: str) -> None:
    """Delete files from directory that match the pattern"""
    dir = settings.BASE_DIR / "backend" / dir
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


@pytest.fixture
def api_client() -> APIClient:
    """Helper object for HTTP requests"""
    return APIClient()


@pytest.fixture
def create_user(django_user_model):
    """Helper function for creating user"""
    return django_user_model.objects.create_user


@pytest.fixture
def regular_user(create_user, api_client):
    """Create and return authenticated user"""
    user = create_user(username="username", password="mypass")
    api_client.force_authenticate(user=user)
    yield user
