from rest_framework import generics, permissions

from . import models, serializers, utils


class AuctionItemList(generics.ListAPIView):
    """View for listing and filtering auction items"""

    queryset = models.AuctionItem.objects.all()
    serializer_class = serializers.AuctionItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = utils.StandardResultsSetPagination

    def get_queryset(self):
        """Retrieve auction items in specific order for the authenticated user"""
        order = self.request.query_params.get("order")

        return self.queryset.order_by(order)


class AuctionItemDetail(generics.RetrieveAPIView):
    """Detail view for auction item object"""

    queryset = models.AuctionItem.objects.all()
    serializer_class = serializers.AuctionItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
