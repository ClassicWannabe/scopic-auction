from collections import OrderedDict
from decimal import Decimal
from datetime import datetime, timezone

from django.db.models import Max
from django.db.models.query import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from . import models
from .exceptions import AuctionItemExpired


class StandardResultsSetPagination(PageNumberPagination):
    """Page number pagination with additional `page size` parameter"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                    ("page_size", self.page_size),
                ]
            )
        )


class BaseBidMixin:
    """
    Mixin thath helps perform necessary checks and changes
    when dealing with `Bid` model
    """

    def user_bid_exists(self, serializer: Serializer, queryset: QuerySet) -> bool:
        """Check if user's bid on the item already exists"""
        user_bid = queryset.filter(
            bidder=self.request.user,
            auction_item=serializer.validated_data["auction_item"],
        )
        return user_bid.exists()

    def auction_ended(
        self, serializer: Serializer, instance: models.Bid = None
    ) -> None:
        """Check if the auction ended to raise an exception"""
        if instance is None:
            auction_item = serializer.validated_data["auction_item"]
        else:
            auction_item = instance.auction_item

        current_date = datetime.now(timezone.utc)

        if auction_item and auction_item.bid_close_date < current_date:
            raise AuctionItemExpired(auction_item.bid_close_date, current_date)

    def bid_amount_too_low(
        self, serializer: Serializer, queryset: QuerySet, instance: models.Bid = None
    ) -> bool:
        """
        Check if user's bid amount is less by 1 USD with the highest bid or
        less than initial bid amount on the item
        """
        if instance is None:
            auction_item = serializer.validated_data["auction_item"]
        else:
            auction_item = instance.auction_item

        bid_amount = serializer.validated_data["bid_amount"]

        item_max_bid = (
            queryset.filter(auction_item=auction_item)
            .aggregate(Max("bid_amount"))
            .get("bid_amount__max")
        )

        if item_max_bid and bid_amount - item_max_bid < 1:
            return True

        if bid_amount < auction_item.init_bid:
            return True

        return False

    def get_current_bid(
        self, queryset: QuerySet, serializer: Serializer, instance: models.Bid = None
    ):
        """Get current bid on the item with the highest bid amount"""
        if instance:
            return queryset.filter(auction_item=instance.auction_item)[0]

        current_bids = queryset.filter(
            auction_item=serializer.validated_data.get("auction_item")
        )
        return current_bids[0] if current_bids.exists() else None

    def deducted_funds(self, user: models.CustomUser) -> Decimal:
        """Calculate user's funds after deduction to make for creating or changing the bid"""
        queryset = self.get_queryset()
        user_bids = queryset.filter(bidder=user).select_related("auction_item")
        user_funds = user.funds

        for bid in user_bids:
            highest_bid = queryset.filter(auction_item=bid.auction_item).order_by(
                "-bid_amount"
            )[0]
            if bid == highest_bid:
                user_funds -= bid.bid_amount

        return user_funds

    def not_enough_funds(
        self, bid_amount: Decimal, user: models.CustomUser, instance: models.Bid = None
    ) -> bool:
        """Check if the user does not have enough funds to make or change the bid"""
        deducted_funds = self.deducted_funds(user)
        cur_bid = bid_amount

        if instance:
            prev_bid = instance.bid_amount

            if deducted_funds - (cur_bid - prev_bid) < 0:
                return True
        else:
            if deducted_funds - cur_bid < 0:
                return True

        return False

    def wrong_max_auto_bid_amount(
        self,
        user: models.CustomUser,
        current_bid: models.Bid,
        bid_amount: Decimal = None,
    ) -> bool:
        """Check if maximum auto bid amount is less than user's bid + 1"""
        if bid_amount and user.max_auto_bid_amount < bid_amount + 1:
            return True
        elif current_bid and user.max_auto_bid_amount < current_bid.bid_amount + 1:
            return True
        return False


class AutoBidMixin(BaseBidMixin):
    """Mixin that helps to implement auto-bidding functionality"""

    def auto_bid(
        self,
        serializer: Serializer,
        queryset: QuerySet,
        instance: models.Bid = None,
        current_bid: models.Bid = None,
    ) -> None:
        """Compare and make necessary changes if another user turned on auto bidding"""
        if instance is None:
            auction_item = serializer.validated_data["auction_item"]
        else:
            auction_item = instance.auction_item

        other_user_auto_bids = (
            queryset.filter(auction_item=auction_item, auto_bidding=True)
            .exclude(bidder=self.request.user)
            .select_related("bidder")
            .order_by("-bidder__max_auto_bid_amount")
        )

        if other_user_auto_bids.exists():
            other_user_auto_bid = other_user_auto_bids[0]

            user_max_auto_bid_amount = self.request.user.max_auto_bid_amount
            other_user_max_auto_bid_amount = (
                other_user_auto_bid.bidder.max_auto_bid_amount
            )

            if user_max_auto_bid_amount > other_user_max_auto_bid_amount:
                self._auto_bid_in_favor_of_requested_user(
                    serializer,
                    user_max_auto_bid_amount,
                    other_user_max_auto_bid_amount,
                    other_user_auto_bid,
                    instance,
                )

            else:
                self._auto_bid_in_favor_of_other_user(
                    user_max_auto_bid_amount,
                    other_user_max_auto_bid_amount,
                    other_user_auto_bid,
                )
        elif current_bid and current_bid.bidder != self.request.user:
            serializer.validated_data["bid_amount"] = current_bid.bid_amount + 1

    def _auto_bid_in_favor_of_requested_user(
        self,
        serializer: Serializer,
        user_max_auto_bid_amount: Decimal,
        other_user_max_auto_bid_amount: Decimal,
        other_user_auto_bid: models.Bid,
        instance: models.Bid,
    ) -> None:
        """Make changes in favor of the user who performed the request"""
        if user_max_auto_bid_amount - other_user_max_auto_bid_amount >= 1:
            serializer.validated_data["bid_amount"] = other_user_max_auto_bid_amount + 1
        else:
            serializer.validated_data["bid_amount"] = user_max_auto_bid_amount

        if not self.not_enough_funds(
            serializer.validated_data["bid_amount"], self.request.user, instance
        ):
            other_user_auto_bid.auto_bidding = False
            other_user_auto_bid.save()

    def _auto_bid_in_favor_of_other_user(
        self,
        user_max_auto_bid_amount: Decimal,
        other_user_max_auto_bid_amount: Decimal,
        other_user_auto_bid: models.Bid,
    ) -> None:
        """Make changes in favor of another user who turned on auto bidding earlier"""
        other_user_auto_bidding = True
        if other_user_max_auto_bid_amount - user_max_auto_bid_amount >= 1:
            other_user_bid_amount = user_max_auto_bid_amount + 1
        else:
            other_user_bid_amount = other_user_max_auto_bid_amount
            other_user_auto_bidding = False

        if not self.not_enough_funds(
            other_user_bid_amount,
            other_user_auto_bid.bidder,
            other_user_auto_bid,
        ):
            other_user_auto_bid.bid_amount = other_user_bid_amount
            other_user_auto_bid.auto_bidding = other_user_auto_bidding
            other_user_auto_bid.save()
