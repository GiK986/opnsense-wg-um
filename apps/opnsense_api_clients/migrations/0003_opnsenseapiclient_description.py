# Generated by Django 4.2.3 on 2023-07-09 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps_opnsense_api_clients", "0002_alter_opnsenseapiclient_api_key_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="opnsenseapiclient",
            name="description",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
