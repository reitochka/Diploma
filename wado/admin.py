from django.contrib import admin
from .models import Patient, Study, Series, Image, Profile
from django.contrib.auth.models import User

class PatientAdmin(admin.ModelAdmin):
    list_display = ('Name','PatientID','BirthDate','Sex','Age')
    search_fields = ('Name', 'PatientID')
    list_filter = ('Name', 'BirthDate',)
    date_hierarchy = 'BirthDate'

class StudyAdmin(admin.ModelAdmin):
    list_display = ('Patient','StudyInstanceUID','StudyID','StudyDate','StudyTime','ModalitiesInStudy', 'InstitutionName',)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('Study','SeriesInstanceUID','Modality','SeriesNumber', 'SOPClassUID', 'Manufacturer', 'JsonURL', 'SeriesDescription', 'BodyPartExamined', 'SeriesDate', 'SeriesTime',)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('Series','InstanceNumber','URL',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('User', 'isMedicalPersonal')

admin.site.register(Patient, PatientAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Profile, ProfileAdmin)
