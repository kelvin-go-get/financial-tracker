from django.contrib import admin
from tracker.models import Category, MonthlySummary, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(MonthlySummary)
