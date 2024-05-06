# Generated by Django 5.0.4 on 2024-04-16 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='currency',
            field=models.CharField(choices=[('GBP', 'British Pound'), ('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', max_length=3),
        ),
    ]