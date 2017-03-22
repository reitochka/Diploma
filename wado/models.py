from django.db import models

class Patient(models.Model):
    PatientID = models.CharField(max_length = 50, blank = True)
    Name = models.CharField(max_length = 20, blank = True)
    BirthDate = models.DateField(blank = True)
    SEX = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    ]
    Sex = models.CharField(max_length=2,
                                      choices=SEX,
                                      default='O')

    def __str__(self):
        return self.Name

class Study(models.Model):
    Patient = models.ForeignKey(
        'Patient',
        on_delete = models.CASCADE,
    )
    StudyInstanceUID = models.CharField(max_length = 50)
    Date = models.DateField(blank = True)
    Time = models.TimeField(blank = True)
    StudyID = models.CharField(max_length = 50, blank = True)
    AccessionNumber = models.CharField(max_length = 50, blank = True)
    ModalitiesInStudy = models.CharField(max_length = 50, blank = True)
    ReferringPhysicianName = models.CharField(max_length = 50, blank = True)
    PerformingPhysicianName = models.CharField(max_length = 50, blank = True)
    NameOfPhysiciansReadingStudy = models.CharField(max_length = 50, blank = True)
    InstitutionalDepartmentName = models.CharField(max_length = 50, blank = True)
    InstitutionName = models.CharField(max_length = 50, blank = True)
    NumberOfStudyRelatedInstances = models.CharField(max_length = 50, blank = True)
    StudyDescription = models.TextField(blank = True)

    class Meta:
        verbose_name_plural = "Studies"

    def __str__(self):
        return self.StudyInstanceUID

class Series(models.Model):
    Study = models.ForeignKey(
        'Study',
        on_delete = models.CASCADE,
    )
    SeriesInstanceUID = models.CharField(max_length = 50)
    Modality = models.CharField(max_length = 50)
    SeriesNumber = models.CharField(max_length = 50, blank = True)

    class Meta:
        verbose_name_plural = "Series"

    def __str__(self):
        return self.SeriesInstanceUID

class Image(models.Model):
    Series = models.ForeignKey(
        'Series',
        on_delete=models.CASCADE,
    )
    URL = models.CharField(max_length=100)
    InstanceNumber = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.InstanceNumber



