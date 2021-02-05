from django import forms
from .import models
from django.utils.translation import ugettext_lazy as _

class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['email', 'firstName', 'lastName', 'street', 'city', 'state', 'zipcode', 'phoneNumber']
        labels = {
            'email': _('Email'),
            'firstName' : _('First Name'),
            'lastName': _('Last Name'),
            'street': _('Street Address'),
            'city': _('City'),
            'state': _('State'),
            'zipcode': _('Zipcode'),
            'phoneNumber': _('Phone Number')
        }

class staffCustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = [ 'firstName', 'lastName', 'phoneNumber']
        labels = {
            'firstName' : _('First Name'),
            'lastName': _('Last Name'),
            'phoneNumber': _('Phone Number')
        }