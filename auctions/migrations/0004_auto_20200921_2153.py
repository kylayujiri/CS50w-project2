# Generated by Django 3.1.1 on 2020-09-21 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200921_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image_link',
            field=models.URLField(blank=True),
        ),
    ]
