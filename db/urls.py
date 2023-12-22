"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from db.views import generator, zadanie_1, zadanie_2, zadanie_3, test

urlpatterns = [
    path('g', generator),
    path('test', test),
    path('z1/<str:search_term>/<int:start_date>/<int:end_date>', zadanie_1),
    path('z2/<int:semester>/<str:year>/', zadanie_2),
    path('z3/<str:group_name>/<str:tag_department>/', zadanie_3),
]
