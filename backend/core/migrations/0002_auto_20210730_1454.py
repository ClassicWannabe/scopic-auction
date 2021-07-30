# Generated by Django 3.2.5 on 2021-07-30 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='auto_bidding',
        ),
        migrations.AddField(
            model_name='bid',
            name='auto_bidding',
            field=models.BooleanField(default=False, verbose_name='auto bidding function'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='max_auto_bid_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='maximum bid amount in USD when auto-bidding is turned on on the item', max_digits=5, verbose_name='max bid amount in USD'),
        ),
    ]
