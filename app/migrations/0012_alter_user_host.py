# Generated by Django 4.2 on 2023-07-17 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_user_host'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guests', to='app.user'),
        ),
    ]
