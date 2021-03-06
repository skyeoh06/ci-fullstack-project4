from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from products.models import Product
import datetime

# Create your models here.


def get_sentinel_user():
    standby_user = get_user_model().objects.get_or_create(username='admin')[0]
    return standby_user


class Household(models.Model):
    """Class defining Household Object"""
    name = models.CharField(blank=False, max_length=50,
                            help_text='Name to identify your household')
    owner = models.ForeignKey(User,
                              blank=False,
                              on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return self.name


class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user")
    household = models.ForeignKey(Household, on_delete=models.CASCADE,
                                  related_name="household")

    def __str__(self):
        return self.user.username


class StorageLocation(models.Model):
    """Location for items in a kitchen. E.g. Cabinet, Fridge"""
    name = models.CharField(blank=False, max_length=50,
                            help_text="Kitchen Fixtures")
    storage_temperature = models.IntegerField(blank=True,
                                              null = True,
                                              help_text="deg Celsius")
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    edited_by = models.ForeignKey(User, blank=False,
                                  on_delete=models.SET(get_sentinel_user))

    STORAGE_TYPE_CHOICES = (
        ('cabinet', 'Cabinet'),
        ('cupboard', 'Cupboard'),
        ('counter-top', 'Counter'),
        ('fridge', 'Refridgerator'),
        ('freezer', 'Freezer'),
        ('pantry', 'Pantry'),
        ('others', 'Others')
    )

    storage_type = models.CharField(blank=False, choices=STORAGE_TYPE_CHOICES,
                                    max_length=11, default="cupboard",
                                    help_text="Storage Location Types")

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    """Food Items to be Stored in Location"""
    food = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(StorageLocation, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, help_text="number of packages")
    remarks = models.TextField(blank=True, max_length=600)
    expiry_date = models.DateField(
        null=True, blank=True, help_text='Enter date in YYYY-MM-DD format')
    threshold = models.IntegerField(blank=False,
                                    help_text="Number of days before expiry"
                                    " date to notify me")
    edited_by = models.ForeignKey(User, blank=False,
                                  on_delete=models.SET(get_sentinel_user))

    PACKAGES = (
        ('bar', 'Bar'),
        ('bottle', 'Bottle'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('roll', 'Roll'),
        ('tin', 'Tin')
    )

    package = models.CharField(blank=False, choices=PACKAGES,
                               max_length=7, default="pack",
                               help_text="Food Packages")

    def __str__(self):
        return f"{self.food} bought by {self.edited_by}"

    def get_food_name(self):
        return self.food.name

    def get_food_image(self):
        return self.food.image

    def get_food_brand(self):
        return self.food.brand

    def get_food_weight(self):
        return self.food.weight_per_pack

    def get_days_duration(self):
        return (self.expiry_date-datetime.date.today()).days

    def get_hit_threshold(self):
        if (self.expiry_date-datetime.date.today()).days <= self.threshold:
            return True
        else:
            return False

    def get_expired(self):
        return (self.expiry_date-datetime.date.today()).days <= 0
