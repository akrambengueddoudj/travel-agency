from django.db import models
from django.contrib.auth.models import User

class TravelPackage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    available_seats = models.IntegerField()

    def __str__(self):
        return self.title

class Reservation(models.Model):
    travel_package = models.ForeignKey(TravelPackage, related_name='reservations', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    number_of_people = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reservation for {self.customer_name}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'