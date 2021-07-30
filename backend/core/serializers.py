from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from . import models


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for custom user objects"""

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "username", "funds", "max_bid_amount")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


class BidSerializer(serializers.ModelSerializer):
    """Serializer for bid objects"""

    class Meta:
        model = models.Bid
        fields = ("bidder", "auction_item", "bid_amount", "auto_bidding")


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
        )
        read_only_fields = ("id", "bidders", "created_date")
