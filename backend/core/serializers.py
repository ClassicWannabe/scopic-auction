from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for custom user objects"""

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "username", "funds", "max_auto_bid_amount")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "id": {"read_only": True},
            "funds": {"read_only": True},
        }


class CreateBidSerializer(serializers.ModelSerializer):
    """Serializer for creating bid objects"""

    class Meta:
        model = models.Bid
        fields = ("id", "bidder", "auction_item", "bid_amount", "auto_bidding")
        read_only_fields = ("id", "bidder")


class UpdateBidSerializer(serializers.ModelSerializer):
    """Serializer for updating bid objects"""

    class Meta:
        model = models.Bid
        fields = ("id", "bidder", "auction_item", "bid_amount", "auto_bidding")
        read_only_fields = ("id", "bidder", "auction_item")


class AuctionItemSerializer(serializers.ModelSerializer):
    """Serializer for auction item objects"""

    class Meta:
        model = models.AuctionItem
        fields = (
            "id",
            "title",
            "description",
            "init_bid",
            "bidders",
            "bid_close_date",
            "created_date",
            "compressed_picture",
            "bids",
        )
        read_only_fields = ("id", "bidders", "created_date", "bid_close_date")
