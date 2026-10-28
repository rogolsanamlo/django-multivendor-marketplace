from django.shortcuts import render
from django.conf import settings

def media_admin(request):
    return {"media_url": settings.MEDIA_URL,}


def index(request):
    return render(request,"main_app/index.html")


def about_us(request):
    return render(request, "main_app/about_us.html")


def contact_us(request):
    return render(request, "main_app/contact_us.html")
