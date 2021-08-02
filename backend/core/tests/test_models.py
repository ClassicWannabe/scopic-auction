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
        picture = SimpleUploadedFile("testfile.jpeg", b"file_content")
        auction_item = models.AuctionItem.objects.create(
            title="title",
            description="description",
            init_bid=2.99,
            bid_close_date="2021-08-02",
            picture=picture,
        )

        item = models.AuctionItem.objects.all()[0]

        assert auction_item.title == item.title
        assert auction_item.description == item.description
        assert Decimal(f"{auction_item.init_bid:.2f}") == item.init_bid
        assert auction_item.picture == item.picture

    def test_auction_item_str(self, create_auction_item):
        """Test `AuctionItem` object string representation"""
        auction_item = create_auction_item(title="My Awesome Title")

        assert str(auction_item) == auction_item.title

    def test_auction_item_order(self, create_auction_item):
        """Test `AuctionItem` objects order"""
        auction_item1 = create_auction_item()
        auction_item2 = create_auction_item()
        auction_item3 = create_auction_item()

        items = models.AuctionItem.objects.all()

        assert items[0] == auction_item3
        assert items[1] == auction_item2
        assert items[2] == auction_item1


class BidTests:
    """Tests for `Bid` model"""

    def test_create_bid_successful(self, create_bid):
        """Test that creation of a new bid is successful"""
        bid = create_bid()

        bids = models.Bid.objects.all()

        assert bid == bids[0]

    def test_bid_str(self, create_bid, django_user_model):
        """Test `Bid` object string representation"""
        user = django_user_model.objects.create(
            username="ClassicWannabe", password="password"
        )
        bid = create_bid(bidder=user)

        assert str(bid) == f"{user.username} (ID: {user.id})"

    def test_bid_order(self, create_bid):
        """Test `Bid` objects order"""
        bid1 = create_bid(bid_amount=10)
        bid2 = create_bid(bid_amount=10.5)
        bid3 = create_bid(bid_amount=1)

        items = models.Bid.objects.all()

        assert items[0] == bid2
        assert items[1] == bid1
        assert items[2] == bid3
