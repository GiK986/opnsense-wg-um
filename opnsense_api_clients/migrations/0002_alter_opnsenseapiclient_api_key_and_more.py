# Generated by Django 4.2 on 2023-04-15 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("opnsense_api_clients", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="opnsenseapiclient",
            name="api_key",
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name="opnsenseapiclient",
            name="api_secret",
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name="opnsenseapiclient",
            name="base_url",
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name="opnsenseapiclient",
            name="endpoint_url",
            field=models.CharField(max_length=150),
        ),
    ]
