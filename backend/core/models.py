from io import BytesIO
from PIL import Image
from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUser(AbstractUser):
    """Custom user model with funds and maximum auto bid amount"""

    username = models.CharField(_("username"), max_length=40, unique=True)
    funds = models.DecimalField(
        _("current funds on the account in USD"),
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    max_auto_bid_amount = models.DecimalField(
        _("max bid amount in USD"),
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_(
            "maximum bid amount in USD when auto-bidding is turned on on the item"
        ),
    )

    REQUIRED_FIELDS = []


class AuctionItem(models.Model):
    """Auction item model to be used for bidding"""

    title = models.CharField(_("item title"), max_length=255)
    description = models.TextField(_("item description"), max_length=1000)
    init_bid = models.DecimalField(
        _("initial bid amount in USD"), max_digits=8, decimal_places=2
    )
    bidders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("current bidders list"),
        related_name="auction_items",
        through="Bid",
    )
    bid_close_date = models.DateTimeField(_("bid close date for the item"))
    created_date = models.DateTimeField(_("item creation date"), auto_now_add=True)
    picture = models.ImageField(_("item picture"), upload_to="auction_items/%Y/%m/%d")
    compressed_picture = models.ImageField(
        _("item compressed picture"), upload_to="auction_items/%Y/%m/%d", blank=True
    )

    _original_picture = None

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_picture = self.picture

    @staticmethod
    def compress(image):
        """Compress image that is more than 1.5 MB size"""
        if image.size > 1.5 * 1024 * 1024:
            im = Image.open(image)
            im_io = BytesIO()
            im.save(im_io, "JPEG", quality=70)
            new_image = File(im_io, name=image.name)
            return new_image
        return image

    def save(self, *args, **kwargs):
        """Save the compressed picture along with the original picture in DB"""
        if self.picture != self._original_picture:
            new_picture = self.compress(self.picture)
            self.compressed_picture = new_picture
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["created_date", "title", "description"]
        verbose_name = _("Auction item")
        verbose_name_plural = _("Auction items")


class Bid(models.Model):
    """Model to record the bid amount of the person"""

    auction_item = models.ForeignKey("AuctionItem", related_name="bids", on_delete=models.CASCADE)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bids", on_delete=models.CASCADE)
    bid_amount = models.DecimalField(
        _("bid amount made by the person in USD"), max_digits=8, decimal_places=2
    )
    auto_bidding = models.BooleanField(_("auto bidding function"), default=False)

    def __str__(self):
        return f"{self.bidder.username} (ID: {self.bidder.id})"

    class Meta:
        ordering = ["-bid_amount"]
        verbose_name = _("Bid")
        verbose_name_plural = _("Bids")
