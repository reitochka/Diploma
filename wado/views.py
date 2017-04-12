from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponseNotFound, HttpResponseForbidden
from django.template import loader
from django.core.exceptions import ValidationError
from . import models, forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django_downloadview import VirtualDownloadView, VirtualFile, TextIteratorIO
import dicom
from dicom.dataset import Dataset
from six import StringIO, b
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django_downloadview import StorageDownloadView
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
import os, tempfile, zipfile
from wsgiref.util import FileWrapper
from matplotlib.image import imsave


storage = FileSystemStorage()
static_path = StorageDownloadView.as_view(storage=storage)

'''import matplotlib.pyplot as plt
plt.imshow(matrix) #Needs to be in row,col order
plt.savefig(filename)'''

@login_required
def index(request):
    text = 'Hello, I''m WADO service'
    context = {'text': text}
    return render(request, 'index.html', context)

@login_required
def search(request):
    series = []
    if  'name' in request.GET and request.GET['name']:
        p = request.GET['name']
        #form = forms.SearchForm(request.GET)
        series = models.Series.objects.filter(Study__Patient__Name__icontains=p)

        #results = models.User.objects.all().filter(name__icontains=form['name'].value(), age__lte=form['age'].value())
    '''else:
        form = forms.SearchForm()'''
    return render(request, 'search.html', {'series': series})

def generate_dcm(ds):
    for i in ds:
        tag = i.tag
        value = i.value
        name = i.name
        temp = tag.__str__() + ': ' + name.__str__() + ' ' + value.__str__() + '\n'
        yield temp
    '''temp = ds.PatientsName
    yield temp.__str__()
    temp = ds.PatientsAge
    yield  temp.__str__()'''


class DICOMDownloadView(LoginRequiredMixin, VirtualDownloadView):
    # def get_file(self):
    #     """Return wrapper on ``six.StringIO`` object."""
    #     ds = dicom.read_file("/home/alice/PycharmProjects/Diploma/wado/file01.dcm")
    #     st = ds.PatientsName
    #     st = st.__str__()
    #     dds = StringIO(st)
    #     file_obj = StringIO(u"Hello world!\n")
    #     file_obj2 = TextIteratorIO(generate_dcm(ds))
    #     #dcm = b(ds)
    #     file = open("/home/alice/PycharmProjects/Diploma/wado/dicom_files/file01.dcm", 'rb')
    #     f = file.read()
    #     return ContentFile(f, name='file.dcm')
    #     '''row = ds[0]
    #     json = {row.tag:{'vr': row.VR, 'value': [row.value]}}'''

    def get_file(self):
        url = self.request.GET['url']
        print(url)
        path = models.Image.objects.filter(URL=url)
        url = path[0]
        url = url.URL
        file = open(url, 'rb')
        f = file.read()
        filename = '01.dcm'
        return ContentFile(f, filename)

    #img = Image.fromarray(arr)
    #img.save("/home/alice/output.png")

def wado_uri(request, token):

    # check if token is not valid

    if not request.GET['requestType']=='WADO':
        return HttpResponseNotFound()
    elif request.user.profile.token != token:
        return HttpResponseForbidden
    else:
        image = models.Image.objects.get(SOPInstanceUID=request.GET['objectUID'])
        # check series and study UIDs
        ds = dicom.read_file(image.URL)
        arr = ds.pixel_array
        wcenter = ds[0x28, 0x1050].value
        wwidth = ds[0x28, 0x1051].value // 2
        temp = tempfile.TemporaryFile()
        filename = ''
        if request.GET['contentType']=='application/dicom' or not request.GET['contentType']:
            print('dicom')
            content = 'application/dicom'
            if request.GET['objectUID'] == 'yes':
                print('need to be anonimized')
            if request.GET('transferSyntax'):
                if request.GET('transferSyntax') == '1.2':
                    print(1)
                if request.GET('transferSyntax') == '1.3':
                    print(2)
                if request.GET('transferSyntax') == '1.4':
                    print(3)
        if request.GET['contentType']=='image/jpg':
            print('jpg')
            content = 'image/jpg'
            imsave(temp, arr, wcenter - wwidth, wcenter + wwidth, 'Greys_r', 'jpeg')

        if request.GET['contentType']=='image/png':
            print('png')
            content = 'image/png'
            imsave(temp, arr, wcenter - wwidth, wcenter + wwidth, 'Greys_r')

        if request.GET['contentType']=='text/html':
            print('html')
            content = 'text/html'
            if request.GET['charset'] == 'UTF-8':
                print('UTF-8')
        if request.GET['contentType'] == 'image/gif':
            print('gif')
            content = 'image/gif'

        len = temp.tell()
        temp.seek(0)
        wrapper = FileWrapper(temp)

        response = HttpResponse(wrapper, content_type=content)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['Content-Length'] = len
        return response


@login_required
def send_zip(request):
    images = models.Image.objects.filter(Series_id=request.GET['id'])
    #path = models.Image.objects.get(id=request.GET['id'])
    #filename = path.URL
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    numero = 0
    for image in images:
        numero += 1
        filename=image.URL
        archive.write(filename, 'file%d.dcm' % numero)
    archive.close()
    len = temp.tell()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=series.zip'
    response['Content-Length'] = len
    #wrapper.seek(0)
    return response

@login_required
def get_jpeg(request):
    path = models.Image.objects.get(id=request.GET['id'])
    url = path.URL
    ds = dicom.read_file(url)
    arr = ds.pixel_array
    wcenter = ds[0x28, 0x1050].value
    wwidth = ds[0x28, 0x1051].value//2

    temp = tempfile.TemporaryFile()
    imsave(temp, arr, wcenter-wwidth, wcenter+wwidth,'Greys_r','jpeg')

    len = temp.tell()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='image/jpg')
    response['Content-Disposition'] = 'attachment; filename=01.jpg'
    response['Content-Length'] = len
    return response

@login_required
def GetDicom(request):
    path = models.Image.objects.get(id=request.GET['id'])
    url = path.URL
    file = open(url, 'rb')
    f = file.read()
    len = file.tell()
    file.seek(0)
    wrapper = FileWrapper(file)
    response = HttpResponse(wrapper, content_type='application/dicom')
    response['Content-Disposition'] = 'attachment; filename=newtest.dcm'
    response['Content-Length'] = len
    return response


@login_required
def advanced_search(request):
    series = []
    modalities_list = ['CR', 'CT', 'DX', 'ECG', 'ES', 'IO', 'MG', 'MR', 'NM', 'OP', 'OT', 'PT', 'PX', 'RF', 'RG', 'SC', 'SR', 'US', 'VL', 'XA', 'XC']
    if request.method == "POST":
        if request.user.profile.isMedicalPersonal:
            modality = []
            form = forms.AdvancedMedicalSearchForm(request.POST)
            series = models.Series.objects.all()
            series = series.filter(Study__Patient__Name__icontains=form['Name'].value())
            series = series.filter(Study__Patient__PatientID__icontains=form['PatientID'].value())
            series = series.filter(Study__Patient__BirthDate__range=(form['BirthDateMin'].value(),form['BirthDateMax'].value()))
            if form['Sex'].value()!='O':
                series = series.filter(Study__Patient__Sex=form['Sex'].value())
            series = series.filter(SeriesDate__range=(form['SeriesDateMin'].value(), form['SeriesDateMax'].value()))
            series = series.filter(SeriesDescription__icontains=form['SeriesDescription'].value())
            series = series.filter(BodyPartExamined__icontains=form['BodyPartExamined'].value())
            series = series.filter(Study__InstitutionName__icontains=form['InstitutionName'].value())
            if not form['AllModalities'].value():
                for item in modalities_list:
                    if form[item].value():
                        modality.append(item)
                if modality:
                    series = series.filter(Modality__in=modality)
        else:
            modality = []
            series = models.Series.objects.all()
            series = series.filter(BodyPartExamined__icontains=form['BodyPartExamined'].value())
            if not form['AllModalities'].value():
                for item in modalities_list:
                    if form[item].value():
                        modality.append(item)
                if modality:
                    series = series.filter(Modality__in=modality)
        #results = models.User.objects.all().filter(name__icontains=form['name'].value(), age__lte=form['age'].value())

    else:
        form = forms.AdvancedMedicalSearchForm()
    return render(request, 'advanced_search.html', {'form': form, 'series': series})

@login_required
def series_detail(request, SeriesInstanceUID):
    #images = []
    series = models.Series.objects.get(SeriesInstanceUID=SeriesInstanceUID)
    images = models.Image.objects.filter(Series_id = series.id)
    ds = dicom.read_file(images[0].URL)
    return  render(request,  'series.html', {'series': series, 'images': images, 'ds': ds})


@login_required
def profile(request):
    msg = ''
    medstatus = False
    if request.method == "POST":
        request.user.set_password(request.POST['new_password'])
        request.user.save()
        msg = 'Password successfully changed!'
    else:
        medstatus = request.user.ProfileAdmin.isMedicalPersonal
    return render(request, 'profile.html', {'msg': msg, 'medstatus': medstatus})


class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"

    # В случае успеха перенаправим на главную.
    success_url = '/'

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")