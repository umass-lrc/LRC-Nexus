from django.contrib import admin


from .models import (
    Payroll,
    PayrollInHR,
    PayrollInHRViaLatePay,
    PayrollNotInHR,
    PayrollNotSigned,
)

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('position', 'week_end', 'status')
    list_filter = ('position', 'week_end', 'status')
    search_fields = ('position', 'week_end', 'status')
    ordering = ('position', 'week_end', 'status')

@admin.register(PayrollInHR)
class PayrollInHRAdmin(admin.ModelAdmin):
    list_display = ('payroll',)
    list_filter = ('payroll',)
    search_fields = ('payroll',)
    ordering = ('payroll',)

@admin.register(PayrollInHRViaLatePay)
class PayrollInHRViaLatePayAdmin(admin.ModelAdmin):
    list_display = ('payroll',)
    list_filter = ('payroll',)
    search_fields = ('payroll',)
    ordering = ('payroll',)

@admin.register(PayrollNotInHR)
class PayrollNotInHRAdmin(admin.ModelAdmin):
    list_display = ('payroll',)
    list_filter = ('payroll',)
    search_fields = ('payroll',)
    ordering = ('payroll',)
    
@admin.register(PayrollNotSigned)
class PayrollNotSignedAdmin(admin.ModelAdmin):
    list_display = ('payroll',)
    list_filter = ('payroll',)
    search_fields = ('payroll',)
    ordering = ('payroll',)
