import pytest

from django.urls import reverse
from rest_framework import status

from core.exceptions import AuctionItemExpired
from core import models

pytestmark = pytest.mark.django_db


class CustomUserViewTests:
    """Tests for `CustomUser` objects view"""

    def test_get_token_successful(self, api_client, create_user):
        """Test obtaining user token is successful"""
        create_user(username="username", password="password")
        url = reverse("core:token")

        response = api_client.post(
            url, {"username": "username", "password": "password"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["token"]) > 0

    def test_get_user_detail(self, api_client, regular_user):
        """Test retrieving user details is successful"""
        url = reverse("core:user")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == regular_user.id

    def test_update_user(self, api_client, regular_user):
        """Test updating the user is successful"""
        url = reverse("core:user")
        payload = {"username": "SomeNewUsername", "email": "mymail@mail.ru"}

        response = api_client.patch(url, payload)

        regular_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert regular_user.username == payload["username"]
        assert regular_user.email == payload["email"]


class AuctionItemViewTests:
    """Tests for `AuctionItem` objects view"""

    def test_list_items_successful(self, api_client, regular_user, create_auction_item):
        """Test listing auction items is successful"""
        url = reverse("core:auctionitem-list")
        item1 = create_auction_item()
        item2 = create_auction_item()

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["id"] in [item1.id, item2.id]
        assert response.data["results"][1]["id"] in [item1.id, item2.id]

    def test_get_item_successful(self, api_client, regular_user, create_auction_item):
        """Test retrieving auction item is successful"""
        item = create_auction_item()
        url = reverse("core:auctionitem-detail", args=[item.id])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == item.id


class CreateBidViewTests:
    """Tests for creating `Bid` objects view"""

    def test_create_bid_successful(self, api_client, regular_user, create_auction_item):
        """Test making a bid is successful"""
        item = create_auction_item(init_bid=5)
        url = reverse("core:bid-list")
        payload = {"auction_item": item.id, "bid_amount": 5}

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["bidder"] == regular_user.id
        assert response.data["auction_item"] == item.id

    def test_create_bid_again_fails(
        self, api_client, regular_user, create_bid, create_auction_item
    ):
        """Test creating second bid with the same user and auction item fails"""
        auction_item = create_auction_item()
        create_bid(bidder=regular_user, auction_item=auction_item)
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": auction_item.init_bid + 1,
        }

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bid already exists"

    def test_create_bid_expired_item_fails(
        self, api_client, regular_user, create_auction_item
    ):
        """Test creating a bid on the item with past `bid_close_date` fails"""
        auction_item = create_auction_item(bid_close_date="2020-01-01")
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": auction_item.init_bid + 1,
        }

        with pytest.raises(AuctionItemExpired):
            api_client.post(url, payload)

    def test_create_low_bid_fails(self, api_client, regular_user, create_auction_item):
        """Test creating a bid with low bid amount fails"""
        auction_item = create_auction_item(init_bid=5)
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": auction_item.init_bid - 0.5,
        }

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bid too low"

    def test_create_low_auto_bid_fails(
        self, api_client, regular_user, create_auction_item
    ):
        """Test creating a bid with auto-bidding and low auto-bid amount fails"""
        auction_item = create_auction_item(init_bid=5)
        regular_user.max_auto_bid_amount = auction_item.init_bid + 1
        regular_user.save()
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": auction_item.init_bid + 1,
            "auto_bidding": True,
        }

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Auto bid amount is too low"

    def test_create_bid_not_enough_funds(
        self, api_client, regular_user, create_auction_item
    ):
        """Test creating a bid having low amount of funds fails"""
        auction_item = create_auction_item(init_bid=5)
        regular_user.funds = auction_item.init_bid - 1
        regular_user.save()
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": auction_item.init_bid,
        }

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Not enough funds"

    def test_create_auto_bid_in_favor_of_this_user(
        self, api_client, regular_user, create_auction_item, create_user, create_bid
    ):
        """Test creating a bid with auto-bidding is in favor of the requested user"""
        auction_item = create_auction_item(init_bid=5)
        other_user = create_user(
            username="other_username",
            password="password",
            funds=10 ** 6,
            max_auto_bid_amount=100,
        )
        other_user_bid = create_bid(
            bidder=other_user,
            auction_item=auction_item,
            auto_bidding=True,
            bid_amount=auction_item.init_bid + 1,
        )
        regular_user.max_auto_bid_amount = 101
        regular_user.save()
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": other_user_bid.bid_amount + 1,
            "auto_bidding": True,
        }

        response = api_client.post(url, payload)

        other_user_bid.refresh_from_db()

        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data["bid_amount"]) == other_user.max_auto_bid_amount + 1
        assert other_user_bid.auto_bidding is False

    def test_create_auto_bid_in_favor_of_other_user(
        self, api_client, regular_user, create_auction_item, create_user, create_bid
    ):
        """
        Test creating a bid with auto-bidding is in favor of another user
        who also turned on auto-bidding
        """
        auction_item = create_auction_item(init_bid=5)
        other_user = create_user(
            username="other_username",
            password="password",
            funds=10 ** 6,
            max_auto_bid_amount=101,
        )
        other_user_bid = create_bid(
            bidder=other_user,
            auction_item=auction_item,
            auto_bidding=True,
            bid_amount=auction_item.init_bid + 1,
        )
        regular_user.max_auto_bid_amount = 100
        regular_user.save()
        url = reverse("core:bid-list")
        payload = {
            "auction_item": auction_item.id,
            "bid_amount": other_user_bid.bid_amount + 1,
            "auto_bidding": True,
        }

        response = api_client.post(url, payload)

        other_user_bid.refresh_from_db()

        user_bid = models.Bid.objects.filter(
            auction_item=auction_item, bidder=regular_user
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bid too low"
        assert other_user_bid.bid_amount == regular_user.max_auto_bid_amount + 1
        assert not user_bid.exists()


class UpdateBidViewTests:
    """Tests for updating `Bid` objects view"""

    def test_update_bid_successful(
        self, api_client, regular_user, create_bid, create_auction_item
    ):
        """Test updating the bid is successful"""
        auction_item = create_auction_item(init_bid=5)
        bid_amount = auction_item.init_bid
        bid = create_bid(
            bidder=regular_user, auction_item=auction_item, bid_amount=bid_amount
        )
        url = reverse("core:bid-detail", args=[bid.id])
        payload = {"bid_amount": bid_amount + 1}

        response = api_client.patch(url, payload)

        bid.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert bid.bid_amount == bid_amount + 1
        assert response.data["bidder"] == regular_user.id
        assert response.data["auction_item"] == auction_item.id

    def test_update_bid_expired_item_fails(
        self, api_client, regular_user, create_auction_item, create_bid
    ):
        """Test updating a bid on the item with past `bid_close_date` fails"""
        auction_item = create_auction_item(bid_close_date="2020-01-01")
        bid = create_bid(bidder=regular_user, auction_item=auction_item)
        url = reverse("core:bid-detail", args=[bid.id])
        payload = {
            "bid_amount": bid.bid_amount + 1,
        }

        with pytest.raises(AuctionItemExpired):
            api_client.patch(url, payload)

    def test_update_low_bid_fails(
        self, api_client, regular_user, create_auction_item, create_bid
    ):
        """Test updating the bid with low or the same bid amount fails"""
        auction_item = create_auction_item()
        bid = create_bid(bidder=regular_user, auction_item=auction_item)
        url = reverse("core:bid-detail", args=[bid.id])
        payload = {
            "bid_amount": bid.bid_amount,
        }

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bid too low"

    def test_update_low_auto_bid_fails(
        self, api_client, regular_user, create_auction_item, create_bid
    ):
        """Test updating the bid with auto-bidding and low auto-bid amount fails"""
        auction_item = create_auction_item()
        bid = create_bid(bidder=regular_user, auction_item=auction_item)
        regular_user.max_auto_bid_amount = auction_item.init_bid
        regular_user.save()
        url = reverse("core:bid-detail", args=[bid.id])
        payload = {"auto_bidding": True}

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Auto bid amount is too low"

    def test_update_bid_not_enough_funds(
        self, api_client, regular_user, create_auction_item, create_bid
    ):
        """Test updating the bid having low amount of funds fails"""
        auction_item = create_auction_item(init_bid=5)
        bid = create_bid(bidder=regular_user, auction_item=auction_item)
        regular_user.funds = auction_item.init_bid
        regular_user.save()
        url = reverse("core:bid-detail", args=[bid.id])
        payload = {
            "bid_amount": auction_item.init_bid + 1,
        }

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Not enough funds"

    def test_update_auto_bid_in_favor_of_this_user(
        self, api_client, regular_user, create_auction_item, create_user, create_bid
    ):
        """Test updating a bid with auto-bidding is in favor of the requested user"""
        auction_item = create_auction_item(init_bid=5)
        other_user = create_user(
            username="other_username",
            password="password",
            funds=10 ** 6,
            max_auto_bid_amount=100,
        )
        other_user_bid = create_bid(
            bidder=other_user,
            auction_item=auction_item,
            auto_bidding=True,
            bid_amount=auction_item.init_bid + 1,
        )
        regular_user_bid = create_bid(bidder=regular_user, auction_item=auction_item)
        regular_user.max_auto_bid_amount = 101
        regular_user.save()
        url = reverse("core:bid-detail", args=[regular_user_bid.id])
        payload = {
            "bid_amount": other_user_bid.bid_amount + 1,
            "auto_bidding": True,
        }

        response = api_client.patch(url, payload)

        other_user_bid.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert float(response.data["bid_amount"]) == other_user.max_auto_bid_amount + 1
        assert other_user_bid.auto_bidding is False

    def test_update_auto_bid_in_favor_of_other_user(
        self, api_client, regular_user, create_auction_item, create_user, create_bid
    ):
        """
        Test updating a bid with auto-bidding is in favor of another user
        who also turned on auto-bidding
        """
        auction_item = create_auction_item(init_bid=5)
        other_user = create_user(
            username="other_username",
            password="password",
            funds=10 ** 6,
            max_auto_bid_amount=101,
        )
        other_user_bid = create_bid(
            bidder=other_user,
            auction_item=auction_item,
            auto_bidding=True,
            bid_amount=auction_item.init_bid + 1,
        )
        regular_user_bid = create_bid(bidder=regular_user, auction_item=auction_item)
        regular_user.max_auto_bid_amount = 100
        regular_user.save()
        url = reverse("core:bid-detail", args=[regular_user_bid.id])
        payload = {
            "bid_amount": other_user_bid.bid_amount + 1,
            "auto_bidding": True,
        }

        response = api_client.patch(url, payload)

        other_user_bid.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Bid too low"
        assert other_user_bid.bid_amount == regular_user.max_auto_bid_amount + 1


class RetrieveBidViewTests:
    """Tests for retrieving `Bid` objects view"""

    def test_get_own_bid_successful(
        self,
        api_client,
        regular_user,
        create_bid,
        create_auction_item,
        reverse_with_query,
    ):
        """Test getting own bid on the item is successful"""
        auction_item = create_auction_item()
        bid = create_bid(bidder=regular_user, auction_item=auction_item)
        url = reverse_with_query(
            "core:bid-get-own-bid", query_kwargs={"auction_item": auction_item.id}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert bid.id == response.data["id"]
        assert response.data["bidder"] == regular_user.id
        assert response.data["auction_item"] == auction_item.id

    def test_get_own_bid_not_found(
        self,
        api_client,
        regular_user,
        create_auction_item,
        reverse_with_query,
    ):
        """
        Test getting own bid on the item is not found
        because no previous bid on the item exists
        """
        auction_item = create_auction_item()
        url = reverse_with_query(
            "core:bid-get-own-bid", query_kwargs={"auction_item": auction_item.id}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
