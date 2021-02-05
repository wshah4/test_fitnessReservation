from django import forms
from .import models
from django.utils.translation import ugettext_lazy as _

class FitnessForm(forms.ModelForm):
    class Meta:
        model = models.FitnessClass
        fields = ['className', 'instructorName', 'dayOfWeek', 'startTime', 'endTime', 'maximumCapacity']
        labels = {
            'className': _('Class Name'),
            'instructorName' : _('Class Instructor Name'),
            'dayOfWeek': _('Days of Week Class held'),
            'startTime': _('Class Start Time'),
            'endTime': _('Class End Time'),
            'maximumCapacity': _('Maximum Participants allowed in class'),
        }