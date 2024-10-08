from django.db import models,transaction
from django.contrib.auth.models import AbstractUser


# Create your models here.

class AddTailors(AbstractUser):
    tailor = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(max_length=10, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True)
    id = models.AutoField(primary_key=True)
    assigned_works = models.IntegerField(default=0)
    pending_works = models.IntegerField(default=0)
    upcoming_works = models.IntegerField(default=0)
    completed_works = models.IntegerField(default=0)

    def __str__(self):
        return str(self.tailor)
  # Convert to string before returning


class Cloth(models.Model):
    name = models.CharField(max_length=100)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    stock_length = models.DecimalField(max_digits=10, decimal_places=2)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Set clothdetails to null in all Add_order instances related to this cloth
        Add_order.objects.filter(clothdetails=self).update(clothdetails=None)
        # Proceed with the actual deletion
        super().delete(*args, **kwargs)

class Customer(models.Model):
    objects = None
    clothdetails = models.ForeignKey(Cloth, on_delete=models.SET_NULL, null=True)
    cloth_name = models.CharField(max_length=100, null=True, blank=True)
    ordered_length = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=False)
    length = models.CharField(max_length=15)
    shoulder = models.CharField(max_length=15)
    cloth = models.CharField(max_length=20, null=True)
    sleeve_sada = models.CharField(max_length=15, null=True)
    sleeve_cuff = models.CharField(max_length=15, null=True)
    center_sleeve = models.CharField(max_length=15, null=True)
    collar_type_image_url = models.CharField(max_length=255, null=True)
    pocket_image_url = models.CharField(max_length=255, null=True)
    collar_measurements = models.CharField(max_length=15,null=True)
    cuff_type_image_url = models.CharField(max_length=255, null=True)
    cuff_measurements = models.CharField(max_length=15,null=True)
    collar_type= models.CharField(max_length=15,null=True)
    pocket_type= models.CharField(max_length=15,null=True)
    cuff_type=models.CharField(max_length=15,null=True)
    sleeve_bottom = models.CharField(max_length=15,null=True)
    regal = models.CharField(max_length=15)
    loose = models.CharField(max_length=15)
    pocket = models.CharField(max_length=15)
    seat = models.CharField(max_length=15, null=True)
    bottom1 = models.CharField(max_length=50)
    BUTTON_CHOICES = [
        ('makfi', 'Makfi'),
        ('makfi_bayyin', 'Makfi Bayyin'),
        ('button_bayyin', 'Button Bayyin'),
        ('makfi_op', 'Makfi OP'),
        ('makfi_op_nice', 'Makfi OP Nice'),
        ('makfi_nice', 'Makfi Nice'),
        ('makfi_zip', 'Makfi Zip'),
        ('dabble_zib', 'Dabble Zib'),
    ]
    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
    )
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    tailor = models.ForeignKey(AddTailors, on_delete=models.SET_NULL, null=True)
    description = models.CharField(blank=True, null=True,max_length=100000)
    model_details = models.CharField(blank=True, null=True, max_length=100000)
    bill_number = models.CharField(max_length=15,null=True)
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        # Add more status choices if needed
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
    )

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    details = models.TextField()
    order_date = models.DateField()
    delivery_date = models.DateField()

    def __str__(self):
        return f"Order for {self.customer.name} - {self.order_date}"



class reception_login(models.Model):
    user_name = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20,null=True)

class admin_login(models.Model):
    username = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20,null=True)


class Add_order(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    clothdetails = models.ForeignKey(Cloth,on_delete=models.SET_NULL, null=True)
    cloth_name = models.CharField(max_length=100, null=True, blank=True)
    ordered_length = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    length = models.CharField(max_length=15)
    shoulder = models.CharField(max_length=15)
    cloth = models.CharField(max_length=20, null=True)
    sleeve_sada = models.CharField(max_length=15, null=True)
    sleeve_cuff = models.CharField(max_length=15, null=True)
    center_sleeve = models.CharField(max_length=15, null=True)
    collar_type_image_url = models.CharField(max_length=255, null=True)
    pocket_image_url = models.CharField(max_length=255, null=True)
    pocket_type= models.CharField(max_length=15,null=True)
    collar_measurements = models.CharField(max_length=15,null=True)
    cuff_type_image_url = models.CharField(max_length=255, null=True)
    cuff_measurements = models.CharField(max_length=15,null=True)
    collar_type= models.CharField(max_length=15,null=True)
    cuff_type=models.CharField(max_length=15,null=True)
    sleeve_bottom = models.CharField(max_length=15,null=True)
    regal = models.CharField(max_length=15)
    loose = models.CharField(max_length=15)
    pocket = models.CharField(max_length=15)
    seat = models.CharField(max_length=15, null=True)
    total_payment = models.CharField(max_length=15, null=True)
    advance_payment = models.CharField(max_length=15, null=True)
    balance_payment = models.CharField(max_length=15, null=True)
    bottom1 = models.CharField(max_length=50)
    BUTTON_CHOICES = [
        ('makfi', 'Makfi'),
        ('makfi_bayyin', 'Makfi Bayyin'),
        ('button_bayyin', 'Button Bayyin'),
        ('makfi_op', 'Makfi OP'),
        ('makfi_op_nice', 'Makfi OP Nice'),
        ('makfi_nice', 'Makfi Nice'),
        ('makfi_zip', 'Makfi Zip'),
        ('dabble_zib', 'Dabble Zib'),
    ]
    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
    )
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    tailor = models.ForeignKey(AddTailors, on_delete=models.SET_NULL, null=True)
    description = models.CharField(blank=True, null=True, max_length=100000)
    model_details = models.CharField(blank=True, null=True, max_length=100000)
    bill_number = models.CharField(max_length=15, null=True)
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        # Add more status choices if needed
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
    )
    pending_or_delivered = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('delivered', 'Delivered')],
        default='pending'  # Set default value here
    )
    is_printed = models.BooleanField(default=False)


class Item(models.Model):
    order_id = models.ForeignKey(Add_order, on_delete=models.CASCADE,null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    item_name = models.CharField(max_length=100, null=True)
    item_quantity = models.PositiveIntegerField(null=True)
    item_price = models.FloatField(null=True)
    total_price = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.item_quantity * self.item_price
        super().save(*args, **kwargs)