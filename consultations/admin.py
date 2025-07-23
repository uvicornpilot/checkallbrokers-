from django.contrib import admin
from .models import LossReport

@admin.register(LossReport)
class LossReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'loss_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')
