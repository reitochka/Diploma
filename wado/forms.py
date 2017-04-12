from django import forms
from django.forms import widgets
import datetime


class SearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Patient Name'}),
    )

class AdvancedMedicalSearchForm(forms.Form):
    PatientID = forms.CharField(max_length=50, required=False, label='Patient name', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Patient ID'}), )
    Name = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': "form-control",'placeholder': 'Patient Name'}), )
    Age = forms.DecimalField(max_digits = 8, decimal_places=5, required=False)
    YEARS = range(1900, 2018)
    BirthDateMin = forms.CharField(initial=datetime.date(1900, 1, 1), widget=forms.TextInput(attrs={'class': "form-control",'type': "date"}))
    BirthDateMax = forms.CharField(initial=datetime.date.today(), widget=forms.TextInput(attrs={'class': "form-control",'type': "date"}))
    SeriesDateMin = forms.CharField(initial=datetime.date(1900, 1, 1),
                                    widget=forms.TextInput(attrs={'class': "form-control", 'type': "date"}))
    SeriesDateMax = forms.CharField(initial=datetime.date.today(),
                                    widget=forms.TextInput(attrs={'class': "form-control", 'type': "date"}))
    SeriesDescription = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Description'}))
    BodyPartExamined = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Body Part'}))
    InstitutionName = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Name of Institution'}))
    AllModalities = forms.BooleanField(initial=True, required=False)
    CR = forms.BooleanField(initial=True, required=False)
    CT = forms.BooleanField(initial=True, required=False)
    DX = forms.BooleanField(initial=True, required=False)
    ECG = forms.BooleanField(initial=True, required=False)
    ES = forms.BooleanField(initial=True, required=False)
    IO = forms.BooleanField(initial=True, required=False)
    MG = forms.BooleanField(initial=True, required=False)
    MR = forms.BooleanField(initial=True, required=False)
    NM = forms.BooleanField(initial=True, required=False)
    OP = forms.BooleanField(initial=True, required=False)
    OT = forms.BooleanField(initial=True, required=False)
    PT = forms.BooleanField(initial=True, required=False)
    PX = forms.BooleanField(initial=True, required=False)
    RF = forms.BooleanField(initial=True, required=False)
    RG = forms.BooleanField(initial=True, required=False)
    SC = forms.BooleanField(initial=True, required=False)
    SR = forms.BooleanField(initial=True, required=False)
    US = forms.BooleanField(initial=True, required=False)
    VL = forms.BooleanField(initial=True, required=False)
    XA = forms.BooleanField(initial=True, required=False)
    XC = forms.BooleanField(initial=True, required=False)









    '''BirthDateMin = forms.DateField(widget=widgets.SelectDateWidget(years=YEARS), required=False, initial=datetime.date(1900, 1, 1))
    BirthDateMax = forms.DateField(widget=widgets.SelectDateWidget(years=YEARS), required=False, initial=datetime.date.today())'''
    SEX = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    ]
    Sex = forms.ChoiceField(choices=SEX, required=False, initial='O', widget=forms.Select(attrs={'class': "form-control"}))
    class Media:
        css = {
            'all': ('css/Journal.css/',)
        }

class AdvancedStudentSearchForm(forms.Form):
    YEARS = range(1900, 2018)
    SeriesDateMin = forms.CharField(initial=datetime.date(1900, 1, 1),
                                   widget=forms.TextInput(attrs={'class': "form-control", 'type': "date"}))
    SeriesDateMax = forms.CharField(initial=datetime.date.today(),
                                   widget=forms.TextInput(attrs={'class': "form-control", 'type': "date"}))