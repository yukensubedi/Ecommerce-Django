# Generated by Django 4.1.4 on 2023-04-13 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_orderplaced_paymentstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='paymentstatus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.khalti'),
        ),
    ]