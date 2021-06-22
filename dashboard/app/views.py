from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, request
from django.core import serializers
from .models import transactions

def index(request):
    senator_transactions = transactions.objects.all()[:10]
    context = {
        "page": "index",
        "transactions": senator_transactions,
    }
    return render(request, 'main/index.html', context)

from json import dumps
from django.http import JsonResponse, HttpResponse

def data(request):
    readings = transactions.objects.all()[:10]
    time = []
    position = []
    name = []
    symbol = []
    party = []
    type = []
    state = []
    for i in readings:
        time.append(i.transaction_date)
        position.append(i.position)
        name.append(i.senatorName)
        symbol.append(i.symbol)
        party.append(i.party)
        state.append(i.state)
        type.append(i.transaction_type)

    dataDictionary = {
        "Transaction Date":time,
        "Position":position,
        "Name":name,
        "Stock Ticker":symbol,
        "Party":party,
        "State":state,
        "Transaction Type":type,
    }
    return JsonResponse(dataDictionary)