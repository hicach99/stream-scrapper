# Generated by Django 4.2 on 2023-07-16 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_visit_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='paypal_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
