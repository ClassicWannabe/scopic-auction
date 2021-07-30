from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class BidInline(admin.StackedInline):
    model = models.Bid
    extra = 0


class AuctionItemAdminForm(forms.ModelForm):
    class Meta:
        model = models.AuctionItem
        exclude = ("compressed_picture",)


@admin.register(models.AuctionItem)
class AuctionItemAdmin(admin.ModelAdmin):
    inlines = [BidInline]
    form = AuctionItemAdminForm
    list_display = ["title", "bid_close_date"]
    search_fields = ["title"]


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    model = models.CustomUser
    filter_horizontal = ("groups",)
    list_display = (
        "username",
        "is_staff",
        "is_active",
    )
    list_editable = ("is_active",)
    search_fields = ("username", "email")
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Auction settings"),
            {"fields": ("funds", "max_auto_bid_amount")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    staff_readonly_fields = (
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
        "last_login",
        "date_joined",
        "funds",
        "max_auto_bid_amount",
    )

    def get_readonly_fields(self, request, obj=None):
        """Specify read only fields for everyone except superuser"""
        if not request.user.is_superuser:
            return self.staff_readonly_fields
        else:
            return super().get_readonly_fields(request, obj)
