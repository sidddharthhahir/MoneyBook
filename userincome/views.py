from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import UserIncome, Source
from userpreferences.models import UserPreferences
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse
# Create your views here.

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            source__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__istartswith=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)
@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)

    paginator = Paginator(income, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreferences.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        'sources': sources
}
    
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    source = Source.objects.all()
    context = {
        'sources': source,
        'values': request.POST
    }
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source')
        date = request.POST.get('date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        if not source:
            messages.error(request, 'Source is required')
            return render(request, 'income/add_income.html', context)

        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, description=description, source=source, date=date)
        messages.success(request, 'Income added successfully')
        return redirect('income')
    return render(request, 'income/add_income.html', context)

def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
       sources = Source.objects.all()
        
      
    
       return render(request, 'income/edit-income.html', context)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        source = request.POST.get('source')
        date = request.POST.get('date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit-income.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/edit-income.html', context)

        if not source:
            messages.error(request, 'source is required')
            return render(request, 'income/edit-income.html', context)

        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'income/edit-income.html', context)

        income.owner=request.user 
        income.amount=amount
        income.description=description 
        income.source=source 
        income.date=date
        income.save()
        messages.success(request, 'Income updated successfully')
        return redirect('income')                                                 

    return render(request, 'income/edit-income.html', context)

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'income removed successfully')
    return redirect('income')

