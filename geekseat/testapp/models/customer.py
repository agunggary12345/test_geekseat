from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=255, null=True)
    user_name = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=255, null=True)

    class Meta:
        managed = True
        db_table = 'customer'
