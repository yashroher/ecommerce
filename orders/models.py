#django libs
from django.db import models
from django.db.models.fields import CharField

#local libs
from accounts.models import Account
from store.models import Product, Variation

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account,on_delete = models.CASCADE)
    payment_id = models.CharField(max_length = 500)
    payment_method = models.CharField(max_length = 100)
    amount_paid = models.CharField(max_length = 100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id 

class Order(models.Model):
    STATUS = (
        ('NEW',"NEW"),
        ('ACCEPTED','ACCEPTED'),
        ('COMPLETED','COMPLETED'),
        ('CANCELLED','CANCELLED'),
    )
    
    user = models.ForeignKey(Account,on_delete = models.SET_NULL,null = True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank = True,null = True)
    order_number = models.CharField(max_length=500)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 12)
    email =  models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=500)
    address_line_2 = models.CharField(max_length=500,blank = True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    order_note = models.CharField(max_length = 200,blank = True)
    order_total = models.FloatField()
    status = models.CharField(max_length=10,choices = STATUS,default="NEW")
    tax = models.FloatField()
    ip = models.CharField(max_length=20,blank = True)
    is_ordered = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.first_name


class OrderProduct(models.Model):
    user = models.ForeignKey(Account,on_delete = models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank = True,null = True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation,on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.product_name