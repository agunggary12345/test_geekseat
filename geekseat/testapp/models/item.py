from django.db import models


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_no = models.CharField(max_length=20, null=True)
    item_name = models.CharField(max_length=50, null=True)
    uom = models.CharField(max_length=10, null=True)
    unit_price = models.FloatField(null=True)

    class Meta:
        managed = True
        db_table = 'item'
