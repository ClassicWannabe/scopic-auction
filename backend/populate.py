import os

# Configure settings for project
# Need to run this before calling models from application!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

# Import settings
django.setup()

from random import randint
from datetime import datetime

from faker import Faker

from django.db import IntegrityError
from django.contrib.auth import get_user_model

from core import models


fakegen = Faker()


def create_users():
    """
    Create 5 users with one superuser.
    Passwords for all users are the same - '123456789'.
    """
    for i in range(1, 6):
        is_superuser = False
        is_staff = False
        funds = randint(50, 100)
        if i == 1:
            is_superuser = True
            is_staff = True
            funds = 1000
        try:
            get_user_model().objects.create_user(
                username=f"user{i}",
                password="123456789",
                is_superuser=is_superuser,
                is_staff=is_staff,
                funds=funds,
            )
        except IntegrityError:
            print("User was already populated")


def populate(N=5):
    """
    Create N entries of auction items
    """

    for _ in range(N):

        fake_title = fakegen.sentence(nb_words=2, variable_nb_words=True)
        fake_description = fakegen.paragraph(nb_sentences=5)
        fake_bid_close_date = fakegen.date_time_between_dates(
            datetime_start=datetime(2021, 8, 3, 11, 0, 0),
            datetime_end=datetime(2021, 8, 8, 11, 0, 0),
        )
        fake_init_bid = randint(10, 90)

        models.AuctionItem.objects.create(
            title=fake_title,
            description=fake_description,
            init_bid=fake_init_bid,
            bid_close_date=fake_bid_close_date,
            picture=f"auction_items/fake-{randint(1,5)}.jpg",
            compressed_picture=f"auction_items/fake-{randint(1,5)}.jpg",
        )


if __name__ == "__main__":
    print("Populating the databases...Please Wait")
    create_users()
    populate(20)
    print("Populating Complete")
