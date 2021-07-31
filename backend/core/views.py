from rest_framework import generics, permissions, mixins, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.request import Request

from . import models, serializers, utils


class CustomUserDetail(generics.RetrieveAPIView):
    """View for retrieving user's own data"""

    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> models.CustomUser:
        """Return the user him/herself"""
        return self.request.user


class AuctionItemViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """View for listing and retrieving (filtered) auction items"""

    queryset = models.AuctionItem.objects.all()
    serializer_class = serializers.AuctionItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = utils.StandardResultsSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description")
    ordering_fields = ("created_date", "init_bid")


class BidViewSet(
    utils.ChangeBidMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """View for retrieving, making and updating a bid"""

    queryset = models.Bid.objects.all()
    serializer_class = serializers.CreateBidSerializer
    permission_classes = (permissions.IsAuthenticated,)
    auction_item_model = models.AuctionItem

    def get_serializer_class(self, *args, **kwargs) -> Serializer:
        """Return appropriate serializer class"""
        if self.action == "update":
            return serializers.UpdateBidSerializer

        return super().get_serializer_class(*args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Ensure that the bid object was created by the user him/herself only once
        and validate provided bid amount for the item
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bid_amount = serializer.validated_data.get("bid_amount", None)
        auto_bidding = serializer.validated_data.get("auto_bidding", None)

        if self.user_bid_exists(serializer, queryset):
            return Response(
                {"message": "Bid already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if auto_bidding:
            if self.wrong_max_auto_bid_amount(self.request.user, bid_amount):
                return Response(
                    {"message": "Auto bid amount is too low"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.auto_bid(serializer, queryset)

        if bid_amount:
            if self.bid_amount_too_low(serializer, queryset):
                return Response(
                    {"message": "Bid too low"}, status=status.HTTP_400_BAD_REQUEST
                )

            if self.not_enough_funds(bid_amount, self.request.user):
                return Response(
                    {"message": "Not enough funds"}, status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer: Serializer) -> None:
        """Save the result to DB assigning the user who performed the request as a bidder"""
        serializer.save(bidder=self.request.user)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update the bid made by the user validating the bid amount
        """
        partial = kwargs.pop("partial", False)
        queryset = self.get_queryset()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        bid_amount = serializer.validated_data.get("bid_amount", None)
        auto_bidding = serializer.validated_data.get("auto_bidding", None)

        if auto_bidding:
            if bid_amount and self.wrong_max_auto_bid_amount(
                self.request.user, bid_amount
            ):
                return Response(
                    {"message": "Auto bid amount is too low"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.auto_bid(serializer, queryset, instance)

        bid_amount = serializer.validated_data.get("bid_amount", None)

        if bid_amount:
            if self.bid_amount_too_low(serializer, queryset, instance):
                return Response(
                    {"message": "Bid too low"}, status=status.HTTP_400_BAD_REQUEST
                )

            if self.not_enough_funds(bid_amount, self.request.user, instance):
                return Response(
                    {"message": "Not enough funds"}, status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
