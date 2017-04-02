from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ValidationError
from . import models, forms
from django.db.models import Q
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required


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

@login_required
def advanced_search(request):
    series = []
    if request.method == "POST":
        form = forms.AdvancedSearchForm(request.POST)
        '''series = models.Series.objects.filter(Study__Patient__Name__icontains=form['name'].value())'''
        if form['Name'].value():
            series = models.Series.objects.filter(Study__Patient__Name__icontains=form['Name'].value())
        if form['PatientID'].value():
            if series:
                series = series.filter(Study__Patient__PatientID__icontains=form['Name'].value())
            else:
                series = models.Series.objects.filter(Study__Patient__PatientID__icontains=form['Name'].value())
        if form['BirthDateMin'].value():
            if series:
                series = series.filter(Study__Patient__BirthDate__range=(form['BirthDateMin'].value(),form['BirthDateMax'].value()))
            else:
                series = models.Series.objects.filter(Study__Patient__BirthDate__range=(form['BirthDateMin'].value(),form['BirthDateMax'].value()))
        if form['Sex'].value()!='O':
            if series:
                series = series.filter(Study__Patient__Sex=form['Sex'].value())
            else:
                series = models.Series.objects.filter(Study__Patient__Sex=form['Sex'].value())
        #results = models.User.objects.all().filter(name__icontains=form['name'].value(), age__lte=form['age'].value())
    else:
        form = forms.AdvancedSearchForm()
    return render(request, 'advanced_search.html', {'form': form, 'series': series})



@login_required
def series_detail(request, SeriesInstanceUID):
    images = []
    series = models.Series.objects.get(SeriesInstanceUID=SeriesInstanceUID)
    images = models.Image.objects.filter(Series_id = series.id)
    return  render(request,  'series.html', {'series': series, 'images': images})


@login_required
def profile(request):
    msg = ''
    if request.method == "POST":
        request.user.set_password(request.POST['new_password'])
        request.user.save()
        msg = 'Password successfully changed!'
    return render(request, 'profile.html', {'msg': msg})


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
    success_url = "/"

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