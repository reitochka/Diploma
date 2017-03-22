from django.contrib import admin
from .models import Patient, Study, Series, Image

class PatientAdmin(admin.ModelAdmin):
    list_display = ('Name','PatientID','BirthDate','Sex',)
    search_fields = ('Name', 'PatientID')
    list_filter = ('Name', 'BirthDate',)
    date_hierarchy = 'BirthDate'

class StudyAdmin(admin.ModelAdmin):
    list_display = ('Patient','StudyInstanceUID','StudyID','Date','Time','ModalitiesInStudy', 'InstitutionName',)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ('Study','SeriesInstanceUID','Modality','SeriesNumber',)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('Series','InstanceNumber','URL',)

admin.site.register(Patient, PatientAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Image, ImageAdmin)
