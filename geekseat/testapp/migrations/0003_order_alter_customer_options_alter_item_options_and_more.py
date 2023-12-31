# Generated by Django 4.2.4 on 2023-08-31 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0002_item_alter_customer_address_alter_customer_password_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_no', models.CharField(max_length=30, null=True)),
                ('order_date', models.DateField()),
                ('order_amount', models.FloatField(default=0, null=True)),
            ],
            options={
                'db_table': 'order',
                'managed': True,
            },
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'managed': True},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='customer',
            table='customer',
        ),
        migrations.AlterModelTable(
            name='item',
            table='item',
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seq', models.SmallIntegerField()),
                ('quantity', models.FloatField(null=True)),
                ('unit_price', models.FloatField(default=0, null=True)),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='testapp.item')),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testapp.order')),
            ],
            options={
                'db_table': 'order_detail',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='customer_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='testapp.customer'),
        ),
        migrations.AddConstraint(
            model_name='orderdetail',
            constraint=models.UniqueConstraint(fields=('order_id', 'seq'), name='idx_unique_order_id_seq'),
        ),
    ]
