from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses
from django.contrib import messages
from django.core.paginator import Paginator
import json
from userpreferences.models import UserPreferences
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expenses.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expenses.objects.filter(
            category__istartswith=search_str, owner=request.user) | Expenses.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expenses.objects.filter(
            description__istartswith=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expenses.objects.filter(owner=request.user)

    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreferences.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expenses(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expenses.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expenses.html', context)

        if not category:
            messages.error(request, 'Category is required')
            return render(request, 'expenses/add_expenses.html', context)

        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/add_expenses.html', context)

        Expenses.objects.create(owner=request.user, amount=amount, description=description, category=category, date=date)
        messages.success(request, 'Expenses added successfully')
        return redirect('expenses')
    return render(request, 'expenses/add_expenses.html', context)

def expense_edit(request, id):
    expense = Expenses.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        
       categories = Category.objects.all()
    
       return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit-expense.html', context)

        if not category:
            messages.error(request, 'Category is required')
            return render(request, 'expenses/edit-expense.html', context)

        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner=request.user 
        expense.amount=amount
        expense.description=description 
        expense.category=category 
        expense.date=date
        expense.save()
        messages.success(request, 'Expenses updated successfully')
        return redirect('expenses')                                                 

    return render(request, 'expenses/edit-expense.html', context)

def delete_expense(request, id):
    expense = Expenses.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expenses removed successfully')
    return redirect('expenses')

def expense_category_summary(request):
    
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expenses.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}
    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))
    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount
    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)
    return JsonResponse({'expense_category': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expenses.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=expenses.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount', 'Description', 'Category', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    rows = Expenses.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=expenses.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    expenses = Expenses.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))
    html_string = render_to_string('expenses/pdf-output.html', {'expenses': expenses, 'total': sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output=open(output.name, 'rb')
        response.write(output.read())
    return response

