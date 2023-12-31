# Generated by Django 4.2.4 on 2023-08-31 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_no', models.CharField(max_length=20, null=True)),
                ('item_name', models.CharField(max_length=50, null=True)),
                ('uom', models.CharField(max_length=10, null=True)),
                ('unit_price', models.FloatField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='password',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
