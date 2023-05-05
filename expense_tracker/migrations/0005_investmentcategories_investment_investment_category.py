# Generated by Django 4.2 on 2023-05-05 01:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("expense_tracker", "0004_alter_category_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvestmentCategories",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="investment",
            name="investment_category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="expense_tracker.investmentcategories",
            ),
            preserve_default=False,
        ),
    ]
