from django.db import models

from datetime import datetime

from .item import Item
from .customer import Customer


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_no = models.CharField(max_length=30, null=True)
    order_date = models.DateField(default=datetime.today, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    order_amount = models.FloatField(null=True, default=0)

    class Meta:
        managed = True
        db_table = 'orders'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    seq = models.SmallIntegerField()
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    quantity = models.FloatField(null=True)
    unit_price = models.FloatField(null=True, default=0)

    class Meta:
        managed = True
        db_table = 'order_detail'

        constraints = [
            models.UniqueConstraint(
                fields=['order_id', 'seq'], name='idx_unique_order_id_seq'
            )
        ]

