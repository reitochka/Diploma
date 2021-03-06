"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<lang>[a-z]{2})/accounts/login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^accounts/register/$', views.RegisterFormView.as_view()),
    url(r'^accounts/logout/$', views.LogoutView.as_view()),
    url(r'^search/', views.search, name='search'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^series/(?P<SeriesInstanceUID>[0-9.]+)/$', views.series_detail, name='series_detail'),
    url(r'^advanced_search/', views.advanced_search, name='advanced_search'),
    url(r'^download', views.DICOMDownloadView.as_view()),
    url(r'^get_dicom/', views.GetDicom, name='GetDicom'),
    url(r'^get_zip/', views.send_zip, name='send_zip'),
    url(r'^get_jpeg/', views.get_jpeg, name='get_jpeg'),
    url(r'^static-path/(?P<path>[a-zA-Z0-9_-]+\.[a-zA-Z0-9]{1,4})$', views.static_path, name='static_path'),
    url(r'^wado/(?P<token>[a-zA-Z0-9.-]+)/', views.wado_uri, name='wado_uri'),
]
