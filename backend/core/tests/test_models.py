from datetime import datetime
from decimal import Decimal
import pytest

from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from core import models

pytestmark = pytest.mark.django_db


class CustomUserTests:
    """Tests for `CustomUser` model"""

    def test_create_user_unique_username_fails(self, create_user):
        """Test creating two users with identical usernames fails"""
        with pytest.raises(IntegrityError):
            create_user(username="username", password="password")
            create_user(username="username", password="password")

    def test_create_user_default_fields_value(self, create_user):
        """
        Test that default `funds` and `max_auto_bid_amount` field values
        are equal to 0
        when creating a new user
        """
        user = create_user(username="username", password="password")

        assert user.funds == 0
        assert user.max_auto_bid_amount == 0

    def test_user_str(self, create_user):
        """Test user string representation"""
        user = create_user(username="username", password="password")

        assert str(user) == f"{user.username} (ID: {user.id})"


class AuctionItemTests:
    """Tests for `AuctionItem` model"""

    def test_create_auction_item_successful(self):
        """Test that creation of a new auction item is successful"""
        picture = SimpleUploadedFile("picture.jpeg", b"file_content")
        auction_item = models.AuctionItem.objects.create(
            title="title",
            description="description",
            init_bid=2.99,
            bid_close_date=datetime.now(),
            picture=picture,
        )

        item = models.AuctionItem.objects.all()[0]

        assert auction_item.title == item.title
        assert auction_item.description == item.description
        assert Decimal(f"{auction_item.init_bid:.2f}") == item.init_bid
        assert auction_item.picture == item.picture

