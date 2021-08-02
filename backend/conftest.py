import re
import os
from uuid import uuid4
import pytest

from django.utils.http import urlencode
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core import models


def sample_auction_item(**params):
    """Create and return `AuctionItem` object"""

    defaults = {
        "title": "title",
        "description": "description",
        "init_bid": 2.99,
        "bid_close_date": "2050-01-01",
        "picture": SimpleUploadedFile("testfile.jpeg", b"file_content"),
    }
    defaults.update(**params)

    return models.AuctionItem.objects.create(**defaults)


def sample_bid(**params):
    """Create and return `Bid` object"""

    defaults = {
        "auction_item": sample_auction_item(),
        "bidder": get_user_model().objects.create(
            username=uuid4(), password="password"
        ),
        "bid_amount": 2.99,
    }
    defaults.update(**params)

    return models.Bid.objects.create(**defaults)


def purge_files(dir: str, pattern: str = r"^testfile.*\.(jpeg|jpg|png|pdf)") -> None:
    """Delete files from directory that match the pattern"""
    dir = settings.BASE_DIR / "backend" / dir
    print(dir)
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def reverse_querystring(
    view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None
):
    """Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    """
    base_url = reverse(
        view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app
    )
    if query_kwargs:
        return f"{base_url}?{urlencode(query_kwargs)}"
    return base_url


@pytest.fixture
def api_client() -> APIClient:
    """Helper fixture for HTTP requests"""
    return APIClient()


@pytest.fixture
def create_user(django_user_model):
    """Helper fixture for creating user"""
    return django_user_model.objects.create_user


@pytest.fixture
def regular_user(create_user, api_client):
    """Fixutre that creates and returns authenticated user"""
    user = create_user(username="username", password="mypass", funds=10 ** 7)
    api_client.force_authenticate(user=user)
    yield user


@pytest.fixture
def create_auction_item():
    """
    Fixture that yields function for creating `AuctionItem` object
    and deletes created media files after test
    """

    yield sample_auction_item

    purge_files("media_root/auction_items")


@pytest.fixture
def create_bid():
    """
    Fixture that yields function for creating `Bid` object
    and deletes created media files after test
    """

    yield sample_bid

    purge_files("media_root/auction_items")


@pytest.fixture
def reverse_with_query():
    """Fixture that returns `reverse_querystring` function"""
    return reverse_querystring
