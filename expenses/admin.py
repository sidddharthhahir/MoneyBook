from django.contrib import admin
from .models import Expenses, Category

class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('owner', 'amount', 'description', 'category', 'date')
    search_fields = ('description', 'category', 'date', 'amount')

    list_per_page = 5


admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Category)