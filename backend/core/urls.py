from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("item-list/", views.AuctionItemList.as_view(), name="item_list"),
    path("item-detail/<int:pk>", views.AuctionItemDetail.as_view(), name="item_detail"),
    path("obtain-token/", obtain_auth_token, name="token"),
]
