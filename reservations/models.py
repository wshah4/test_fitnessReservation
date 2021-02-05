from django.db import models
from fitnessClass.models import FitnessClass
from accounts.models import Customer

class WaitList(models.Model):
    wait = models.CharField(max_length=20, null=True)

# Create your models here.
class Reservation(models.Model):
    classReserved = models.ForeignKey(FitnessClass, default=None, on_delete=models.CASCADE)
    customerReserving = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    classDate = models.DateField(default=None)
    reservationStatus = models.CharField(max_length=20, default=None)
    reservationDate = models.DateField(default=None)
    reservationTime = models.TimeField(default=None)
    waitNumber = models.IntegerField(default='0')

    # Reservation Date = {self.reservationDate}, Reservation Time = {self.reservationTime}
    def __str__(self):
        return f'Class Reserved = {self.classReserved}, Customer Reserving {self.customerReserving}, Class Date = {self.classDate}, waitNumber = {self.waitNumber}'