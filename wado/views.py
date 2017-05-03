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
import pydicom
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
from scipy.misc import toimage
import datetime
import uuid
from django.utils import timezone
import imageio
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



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
    profile = []
    try:
        profile = models.Profile.objects.get(Token=token)
    except models.Profile.DoesNotExist:
        return HttpResponseForbidden()
    if not profile.isMedicalPersonal:
        print('-----------------')
        print(profile.Token)
        print(profile.isMedicalPersonal)
        print('TOKEN IS NOT VALID, GO AWAY')
        print('-----------------')
        return HttpResponseForbidden()
    elif  not 'requestType' in request.GET or not request.GET['requestType']=='WADO':
        print ('THERE IS NO requestType')
        return HttpResponseNotFound()
    elif not 'objectUID' in request.GET:
        print ('THERE IS NO objectUID')
        return HttpResponseNotFound()
    else:
        try:
            image = models.Image.objects.get(SOPInstanceUID=request.GET['objectUID'])
        except models.Image.DoesNotExist:
            return HttpResponseNotFound('404.html')
        print('---------------')
        print(request.GET['objectUID'])
        print('---------------')
        # check series and study UIDs
        ds = pydicom.read_file(image.URL)
        arr = ds.pixel_array
        wcenter = ds[0x28, 0x1050].value
        wwidth = ds[0x28, 0x1051].value // 2
        temp = tempfile.TemporaryFile()
        filename = 'WADO_URI'
        if not 'contentType' in request.GET or request.GET['contentType']=='application/dicom':
            print('dicom')
            content = 'application/dicom'
            filename += '.dcm'
            if 'anonimize' in request.GET and request.GET['anonimize'] == 'yes':
                print('need to be anonimized')
                ds = Anonymize(ds)
            if 'transferSyntax' in request.GET and request.GET('transferSyntax'):

                ''' 1.2.840.10008.1.2	Implicit VR Endian: Default Transfer Syntax for DICOM
                    1.2.840.10008.1.2.1	Explicit VR Little Endian
                    1.2.840.10008.1.2.2	Explicit VR Big Endian'''

                if request.GET('transferSyntax') == '1.2.840.10008.1.2':
                    print('Implicit VR Endian: Default')
                    ds.is_implicit_VR
            ds.save_as(temp)
        elif 'contentType' in request.GET:
            if request.GET['contentType']=='image/jpeg':
                print('jpg')
                content = 'image/jpeg'
                filename += '.jpg'
                if 'windowCenter' in request.GET:
                    wcenter = int(request.GET['windowCenter'])
                else:
                    wcenter = ds[0x28, 0x1050].value
                if 'windowWidth' in request.GET:
                    wwidth = int(request.GET['windowWidth']) // 2
                else:
                    wwidth = ds[0x28, 0x1051].value // 2
                sci = toimage(arr, cmin=wcenter - wwidth, cmax=wcenter + wwidth)
                sci.save(temp, 'jpeg')
            elif request.GET['contentType']=='image/png':
                print('png')
                filename += '.png'
                content = 'image/png'
                if 'windowCenter' in request.GET:
                    wcenter = int(request.GET['windowCenter'])
                else:
                    wcenter = ds[0x28, 0x1050].value

                if 'windowWidth' in request.GET:
                    wwidth = int(request.GET['windowWidth']) // 2
                else:
                    wwidth = ds[0x28, 0x1051].value // 2
                imsave(temp, arr, wcenter - wwidth, wcenter + wwidth, 'Greys_r', 'png')
            elif request.GET['contentType']=='text/html':
                print('html')
                content = 'text/html'
                if request.GET['charset'] == 'UTF-8':
                    print('UTF-8')
            elif request.GET['contentType'] == 'image/gif':
                imageio.mimsave('e.gif', arr)
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
    response = HttpResponse()
    if request.method == "POST":
        list = request.POST.getlist('dict')
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        for item in list:
            print(item)
            images = models.Image.objects.filter(Series_id=item)
            series = models.Series.objects.get(id = item)
            ser = series.SeriesInstanceUID
            numero = 0
            for image in images:
                numero += 1
                filename = image.URL
                archive.write(filename, 'series_%s//file%d.dcm' % (ser, numero))
        archive.close()
    else:
        images = models.Image.objects.filter(Series_id=request.GET['id'])
        #path = models.Image.objects.get(id=request.GET['id'])
        #filename = path.URL
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        numero = 0
        for image in images:
            numero += 1
            filename=image.URL
            archive.write(filename, 'dir//file%d.dcm' % numero)
        archive.close()
        #wrapper.seek(0)
    len = temp.tell()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=series.zip'
    response['Content-Length'] = len
    return response

@login_required
def get_jpeg(request):
    path = models.Image.objects.get(id=request.GET['id'])
    url = path.URL
    ds = pydicom.read_file(url)
    #dss = dicom.read_file(url)
    #dss.group_dataset()
    arr = ds.pixel_array
    wcenter = ds[0x28, 0x1050].value
    wwidth = ds[0x28, 0x1051].value//2

    temp = tempfile.TemporaryFile()

    sci = toimage(arr, cmin=wcenter-wwidth, cmax=wcenter+wwidth)
    sci.save(temp, 'jpeg')
    #imsave(temp, arr, wcenter-wwidth, wcenter+wwidth, 'pink')

    len = temp.tell()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='image/jpeg')
    response['Content-Disposition'] = 'attachment; filename=01.jpg'
    response['Content-Length'] = len
    return response

'''i = Image.open('image.png')
imgSize = i.size
rawData = i.tostring()
img = Image.fromstring('L', imgSize, rawData)
img.save('lmode.png')

import numpy as np
from PIL import Image
from rawkit.raw import Raw
filename = '/path/to/your/image.cr2'
raw_image = Raw(filename)
buffered_image = np.array(raw_image.to_buffer())
image = Image.frombytes('RGB', (raw_image.metadata.width, raw_image.metadata.height), buffered_image)
image.save('/path/to/your/new/image.png', format='jpeg')'''


'''import imageio
images = []
for filename in filenames:
    images.append(imageio.imread(filename))
imageio.mimsave('/path/to/movie.gif', images)


with imageio.get_writer('/path/to/movie.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)


>>> f = NamedTemporaryFile(delete=False)
>>> f.name
'/tmp/tmptjujjt'
>>> f.write(b"Hello World!\n")
13
>>> f.close()
>>> os.unlink(f.name)
>>> os.path.exists(f.name)
False'''

'''(0002,0003) Media Storage SOP Instance UID
(0002,0012) Implementation Class UID
(0008,0018) SOP Instance UID
(0008,0020) Study Date
(0008,0030) Study Time
(0008,0021) Series Date
(0008,0031) Series Time
(0008,0022) Acquisition Date
(0008,0032) Acquisition Time
(0008,0023) Content Date
(0008,0033) Content Time
(0008,0080) Institution Name
(0008,0081) Institution Address
(0008,0090) Referring Physician’s Name
(0008,1040) Institutional Department Name
(0018,1030) Protocol Name
(0020,000D) Study Instance UID
(0020,000E) Series Instance UID
(0020,0010) Study ID
(0010,0010) Patient’s Name
(0010,0020) Patient ID
(0010,0030) Patient’s Birth Date
(0010,0032) Patient’s Birth Time
(0010,1040) Patient’s Address
(0008,0050) Accession Number

valid_until = profile.Valid_date.date().strftime("%d %B %Y")'''

def Anonymize(ds):
    random.seed()
    dur_date = ''
    dur_time = random.randint(0, 86399)
    anonymizing_tags = [(0x10,0x10),(0x10,0x20),(0x10,0x40),(0x8, 0x80), (0x8, 0x81), (0x8, 0x90), (0x20, 0x10), (0x8, 0x80), (0x8, 0x50)]
    good_private_tags = [(0x10,0x40),(0x10,0x1010)]

    objectUID = ds[0x8, 0x18].value
    seriesUID = ds[0x20, 0xe].value
    studyUID = ds[0x20, 0xd].value

    image = models.Image.objects.get(SOPInstanceUID=objectUID)
    serie = models.Series.objects.get(SeriesInstanceUID=seriesUID)
    study = models.Study.objects.get(StudyInstanceUID=studyUID)

    if (0x8, 0x20) in ds:
        date = ds[0x8, 0x20].value
        min = datetime.date(1989, 1, 1) - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
        max = datetime.date.today() - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
        dur_date = random.randint(min.days, max.days)
    elif (0x8, 0x21) in ds:
        date = ds[0x8, 0x21].value
        min = datetime.date(1989, 1, 1) - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
        max = datetime.date.today() - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
        dur_date = random.randint(min.days, max.days)
    for item in ds:
            # Изменение всех элементов типа Дата на константу dur_date
            if item.VR == 'DA':
                print(item.name)
                if not dur_date:
                    date = item.value
                    min = datetime.date(1989, 1, 1) - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
                    max = datetime.date.today() - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
                    dur_date = random.randint(min.days, max.days)
                date = item.value
                date = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8]))
                date = date + datetime.timedelta(days=dur_date)
                item.value = date.strftime('%Y%m%d')
            # Изменение всех элементов типа Время на константу dur_time
            elif item.VR == 'TM':
                print(item.name)
                time = item.value
                time = datetime.time(int(time[:2]), int(time[2:4]), int(time[4:6]), int(time[7:10]))
                date = datetime.datetime.combine(datetime.datetime.today(),time)
                date = date + datetime.timedelta(seconds=dur_time)
                time = date.time()
                str = time.strftime('%H%M%S.%f')
                if len(str) == 13:
                    str = str[:7]+str[10:]
                item.value = str
            # Замена элеметов из группы, относящейся к информации о пациенте, всех персональных имен и перечисленных элементов на Anonymized
            elif (item in ds.group_dataset(0x10) and not item.tag in good_private_tags) or item.VR == 'PN' or item.tag in anonymizing_tags:
                item.value = 'Anonymized'
            #Замена уникальных идентификаторов на созданные ранее и хранившиеся в базе данных
            elif item.tag == (0x2, 0x3):
                ds[0x2, 0x3].value = image.AnonimizedInstanceUID  # Media Storage SOP Instance UID
            elif item.tag == (0x8, 0x18):
                ds[0x8, 0x18].value = image.AnonimizedInstanceUID  # SOP Instance UID
            elif item.tag == (0x20, 0xe):
                ds[0x20, 0xe].value = serie.AnonimizedSeriesUID  # Series Instance UID
            elif item.tag == (0x20, 0xd):
                ds[0x20, 0xd].value = study.AnonimizedStudyUID  # Study Instance UID
            elif item.tag == (0x20, 0x52):
                ds[0x20, 0x52].value = image.AnonimizedInstanceUID + '27' # Frame of Reference UID
            elif  item.tag.is_private:
                del item

    return ds


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
            if form.is_valid():
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
                    #print(modality)
                    if modality:
                        series = series.filter(Modality__in=modality)
        else:
            form = forms.AdvancedMedicalSearchForm(request.POST)
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

    # пагинатор
    paginator = Paginator(series, 3)  # Show 5 contacts per page

    page = request.GET.get('page')
    try:
        series = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        series = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        series = paginator.page(paginator.num_pages)

    return render(request, 'advanced_search.html', {'form': form, 'series': series})

@login_required
def series_detail(request, SeriesInstanceUID):
    #images = []
    series = models.Series.objects.get(SeriesInstanceUID=SeriesInstanceUID)
    images = models.Image.objects.filter(Series = series)
    ds = pydicom.read_file(images[0].URL)
    return  render(request,  'series.html', {'series': series, 'images': images, 'ds': ds})


@login_required
def profile(request):
    now = timezone.now()
    msg = []
    profile = models.Profile.objects.get(User=request.user)
    NotValid = False
    token = ''
    valid_until = ''
    if request.method == "POST":
        if 'new_password' in request.POST:
            request.user.set_password(request.POST['new_password'])
            request.user.save()
            msg['password'] = 'Password successfully changed!'
        elif request.method == "POST" and 'days' in request.POST and profile.isMedicalPersonal:
            if (profile.Valid_date - now) < datetime.timedelta(seconds=1):
                profile.Valid_date = now+datetime.timedelta(days=int(request.POST['days']))
                profile.Token = uuid.uuid1()
                profile.save()
                token = profile.Token
                valid_until = profile.Valid_date.date().strftime("%d %B %Y")
            else:
                msg['still_valid'] = 'Token is still valid'
                token = profile.Token
                valid_until = profile.Valid_date.date().strftime("%d %B %Y")
    else:
        NotValid = (profile.Valid_date - now) < datetime.timedelta(seconds=1)
        if not NotValid:
            token = profile.Token
            valid_until = profile.Valid_date.date().strftime("%d %B %Y")

    return render(request, 'profile.html', {'msg': msg, 'NotValid': NotValid, 'token': token, 'valid_until': valid_until})


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


def generate_UID():
    random.seed()
    result = []
    res = str(uuid.uuid4().int) + str(uuid.uuid4().int)
    ranges = [(1, 3), (1, 2), (1, 3), (4, 6), (5, 10), (1, 2), (1, 3), (1, 3), (5, 10), (4, 6), (4, 5), (4, 5)]

    # генерируем массив частей идентификатора
    for item in ranges:
        print(item)
        rand = random.randint(item[0], item[1])
        while res[rand] == '0':
            print('found zero')
            rand += 1
        print('now %d symbols' % rand)
        result.append(res[:rand])
        res = res[rand:]

    # необходимо, чтобы суммарно символов было не больше 63 (цифр не больше 52)
    sum = 0
    for item in result:
        sum += len(item)

    while sum > 52:
        rand1 = random.randint(0, 11)
        if len(result[rand1]) > 2:
            temp = result[rand1]
            rand2 = random.randint(1, len(temp) - 1)
            temp = temp[:rand2] + temp[rand2 + 1:]
            result[rand1] = temp
        sum = 0
        for item in result:
            sum += len(item)

    uid = ''
    for i in range(len(result)-1):
        uid += result[i] + '.'
    uid += result[len(result)-1]



