from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    email = models.EmailField(max_length=50, null=True)
    firstName = models.CharField(max_length=20, null=True)
    lastName = models.CharField(max_length=20, null=True)
    street = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=20, null=True)
    zipcode = models.CharField(max_length=20, null=True)
    phoneNumber = models.CharField(max_length=20, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    verificationChoices = [
        ('Annual', 'Annual Pass Holder'),
        ('Resident', 'Town of Leesburg Resident'),
        ('Neither', 'Neither'),
        ('UnVerified', 'UnVerified')
    ]
    verified = models.CharField(max_length=20, choices=verificationChoices)

    def __str__ (self):
        return f'{self.firstName} {self.lastName}'