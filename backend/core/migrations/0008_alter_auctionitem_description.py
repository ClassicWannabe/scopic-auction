# Generated by Django 3.2.5 on 2021-08-01 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_alter_bid_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auctionitem",
            name="description",
            field=models.TextField(max_length=3000, verbose_name="item description"),
        ),
    ]
