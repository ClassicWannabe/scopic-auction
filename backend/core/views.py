from rest_framework import generics, permissions, mixins, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.request import Request

from . import models, serializers, utils


class CustomUserDetail(generics.RetrieveAPIView, generics.UpdateAPIView):
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
    utils.AutoBidMixin,
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

    def get_object_for_user(self) -> models.Bid:
        """Return `Bid` object pertaining to the requested user"""
        queryset = self.get_queryset()
        auction_item_id = self.request.GET.get("auction_item")
        obj = generics.get_object_or_404(
            queryset, bidder=self.request.user, auction_item__id=auction_item_id
        )

        self.check_object_permissions(self.request, obj)

        return obj

    @action(detail=False, methods=["get"], url_path="own-bid")
    def get_own_bid(self, request: Request, *args, **kwargs) -> Response:
        """Retrieve user's bid on the specific auction item"""
        instance = self.get_object_for_user()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

        self.auction_ended(serializer)

        current_bid = self.get_current_bid(queryset, serializer)
        bid_amount = serializer.validated_data.get("bid_amount", None)
        auto_bidding = serializer.validated_data.get("auto_bidding", None)

        if self.user_bid_exists(serializer, queryset):
            return Response(
                {"message": "Bid already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if self.wrong_max_auto_bid_amount(
            self.request.user, current_bid, auto_bidding, bid_amount
        ):
            return Response(
                {"message": "Auto bid amount is too low"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.auto_bid(serializer, queryset, auto_bidding, current_bid=current_bid)

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

        self.auction_ended(serializer, instance)

        current_bid = self.get_current_bid(queryset, serializer, instance)
        bid_amount = serializer.validated_data.get("bid_amount", None)
        auto_bidding = serializer.validated_data.get("auto_bidding", None)

        if self.wrong_max_auto_bid_amount(
            self.request.user, current_bid, auto_bidding, bid_amount
        ):
            return Response(
                {"message": "Auto bid amount is too low"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.auto_bid(serializer, queryset, auto_bidding, instance, current_bid)

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
