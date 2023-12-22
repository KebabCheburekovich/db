from django.http import HttpResponse
from django.shortcuts import render

from db.generator import gen, z1, z2, z3, test_p


def test(request):
    test_p()
    return HttpResponse()


def generator(request):
    gen()
    print("Generate success")
    return HttpResponse("Generate success")


def zadanie_1(request, search_term, start_date, end_date):
    return HttpResponse(z1(search_term, start_date, end_date), content_type="text/plain; charset=utf-8")


def zadanie_2(request, semester, year):
    return HttpResponse(z2(semester, year), content_type="text/plain; charset=utf-8")


def zadanie_3(request, group_name, tag_department):
    return HttpResponse(z3(group_name, tag_department), content_type="text/plain; charset=utf-8")
