from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

router = DefaultRouter()
router.register("bids", views.BidViewSet)
router.register("items", views.AuctionItemViewSet)

app_name = "core"

urlpatterns = [
    path("obtain-token/", obtain_auth_token, name="token"),
    path("user-detail/", views.CustomUserDetail.as_view(), name="user_detail"),
    path("", include(router.urls)),
]
