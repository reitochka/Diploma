from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

class Patient(models.Model):
    PatientID = models.CharField(max_length = 50, blank = True)
    Name = models.CharField(max_length = 20, blank = True)
    BirthDate = models.DateField(blank = True)
    Age = models.DurationField(blank=True, null=True)
    #Age = models.DecimalField(max_digits = 8, decimal_places=5, blank=True, null=True,)
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

class Profile(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    isMedicalPersonal = models.BooleanField(default=False)
    Token = models.CharField(max_length=200, blank=True)
    Valid_date = models.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=1))

    @receiver(post_save, sender=User)
    def create_user_Profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_Profile(sender, instance, **kwargs):
        instance.Profile.save()

    class Meta:
        verbose_name_plural = "Profiles"

    def __str__(self):
        return str(self.isMedicalPersonal)

class Study(models.Model):
    Patient = models.ForeignKey(
        'Patient',
        on_delete = models.CASCADE,
    )
    StudyInstanceUID = models.CharField(max_length = 50, unique=True)
    AnonimizedStudyUID = models.CharField(max_length = 50, blank=True)
    StudyDate = models.DateField(blank = True)
    StudyTime = models.TimeField(blank = True)
    StudyID = models.CharField(max_length = 50, blank = True)
    AccessionNumber = models.CharField(max_length = 50, blank = True)
    ModalitiesInStudy = models.CharField(max_length = 50, blank = True)
    ReferringPhysicianName = models.CharField(max_length = 50, blank = True)
    PerformingPhysicianName = models.CharField(max_length = 50, blank = True)
    NameOfPhysiciansReadingStudy = models.CharField(max_length = 50, blank = True)
    InstitutionalDepartmentName = models.CharField(max_length = 50, blank = True)
    InstitutionName = models.CharField(max_length = 50, blank = True)
    NumberOfStudyRelatedInstances = models.CharField(max_length = 50, blank = True)
    StudyDescription = models.TextField(max_length=1000, blank = True)

    class Meta:
        verbose_name_plural = "Studies"

    def __str__(self):
        return self.StudyInstanceUID

class Series(models.Model):
    Study = models.ForeignKey('Study',on_delete = models.CASCADE,)
    SeriesInstanceUID = models.CharField(max_length = 50, unique=True)
    AnonimizedSeriesUID = models.CharField(max_length=50, unique=True)
    SeriesDate = models.DateField(blank=True)
    SeriesTime = models.TimeField(blank=True)
    Modality = models.CharField(max_length = 10)
    SeriesNumber = models.PositiveSmallIntegerField(null=True, blank=True) #models.CharField(max_length = 50, blank = True)
    SOPClassUID = models.CharField(max_length = 10, blank=True)
    Manufacturer = models.CharField(max_length = 10, blank=True)
    JsonURL = models.CharField(max_length=200, blank=True) #unique later
    SeriesDescription = models.TextField(max_length=1000, blank=True)
    BodyPartExamined = models.CharField(max_length = 10, blank=True)

    class Meta:
        verbose_name_plural = "Series"

    def __str__(self):
        return self.SeriesInstanceUID

class Image(models.Model):
    Series = models.ForeignKey('Series', on_delete=models.CASCADE,)
    SOPInstanceUID = models.CharField(max_length=50, unique=True)
    AnonimizedInstanceUID = models.CharField(max_length=50, unique=True)
    URL = models.CharField(max_length=200, unique=True)
    InstanceNumber = models.PositiveSmallIntegerField(blank=True) # models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.SOPInstanceUID





