from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    text = 'Hello, I''m WADO service'
    context = {'text': text}
    return render(request, 'index.html', context)