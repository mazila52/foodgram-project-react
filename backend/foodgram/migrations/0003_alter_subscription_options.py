# Generated by Django 4.0.3 on 2022-07-11 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('subscribed_to',), 'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
    ]
