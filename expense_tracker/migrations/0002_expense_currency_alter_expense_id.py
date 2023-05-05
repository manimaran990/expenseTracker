# Generated by Django 4.2 on 2023-05-04 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense_tracker", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="currency",
            field=models.CharField(
                choices=[("CAD", "Canadian Dollar"), ("INR", "Indian Rupee")],
                default="CAD",
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="expense",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
