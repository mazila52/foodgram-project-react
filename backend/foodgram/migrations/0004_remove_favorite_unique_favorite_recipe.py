# Generated by Django 4.0.3 on 2022-07-12 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0003_alter_subscription_options'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_recipe',
        ),
    ]
