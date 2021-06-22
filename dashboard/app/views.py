from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, request
from django.core import serializers
from .models import transactions

def index(request):
    senator_transactions = transactions.objects.all()
    context = {
        "page": "index",
        "transactions": senator_transactions,
    }
    return render(request, 'main/index.html', context)

from json import dumps
from django.http import JsonResponse, HttpResponse

def data(request):
    readings = transactions.objects.all()
    print(readings)
    date = []
    senatorname = []
    symbol = []
    party = []
    type = []
    state = []
    for i in readings:
        date.append(i.transaction_date)
    for i in readings:
        senatorname.append(i.senatorName)
    for i in readings:
        symbol.append(i.symbol)
    for i in readings:
        party.append(i.party)
    for i in readings:
        state.append(i.state)
    for i in readings:
        type.append(i.transaction_type)

    dataDictionary = {
        "Transaction Date":date,
        "Name":senatorname,
        "Stock Ticker":symbol,
        "Party":party,
        "State":state,
        "Transaction Type":type,
    }
    return JsonResponse(dataDictionary)