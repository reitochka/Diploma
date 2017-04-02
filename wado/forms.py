from django import forms
from django.forms import widgets
import datetime


class SearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Patient Name'}),
    )

class AdvancedSearchForm(forms.Form):
    PatientID = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Patient ID'}),
    )
    Name = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': 'Patient Name'}),
    )
    YEARS = range(1900, 2018)
    BirthDateMin = forms.DateField(widget=widgets.SelectDateWidget(years=YEARS), required=False, initial=datetime.date(1900, 1, 1))
    BirthDateMax = forms.DateField(widget=widgets.SelectDateWidget(years=YEARS), required=False, initial=datetime.date.today())
    SEX = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    ]
    Sex = forms.ChoiceField(choices=SEX, required=False, initial='O')
    class Media:
        css = {
            'all': ('css/Readable.css/',)
        }
