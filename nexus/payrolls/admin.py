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
    list_filter = ('status', 'week_end', 'position__semester')
    search_fields = ('position__user__first_name', 'position__user__last_name', 'position__user__email')
    ordering = ('-week_end', 'position')
    list_per_page = 50  # Show only 50 records per page
    date_hierarchy = 'week_end'  # Add date-based navigation
    list_select_related = ('position', 'position__user', 'position__semester')  # Optimize queries
    
    def get_queryset(self, request):
        # Optimize the queryset to avoid N+1 queries
        return super().get_queryset(request).select_related(
            'position', 
            'position__user', 
            'position__semester'
        )

@admin.register(PayrollInHR)
class PayrollInHRAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'get_week_end', 'get_position')
    list_filter = ('payroll__status', 'payroll__week_end')
    search_fields = ('payroll__position__user__first_name', 'payroll__position__user__last_name')
    ordering = ('-payroll__week_end',)
    list_per_page = 50
    list_select_related = ('payroll', 'payroll__position', 'payroll__position__user')
    
    def get_week_end(self, obj):
        return obj.payroll.week_end
    get_week_end.short_description = 'Week End'
    get_week_end.admin_order_field = 'payroll__week_end'
    
    def get_position(self, obj):
        return obj.payroll.position
    get_position.short_description = 'Position'
    get_position.admin_order_field = 'payroll__position'

@admin.register(PayrollInHRViaLatePay)
class PayrollInHRViaLatePayAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'get_week_end', 'get_position')
    list_filter = ('payroll__status', 'payroll__week_end')
    search_fields = ('payroll__position__user__first_name', 'payroll__position__user__last_name')
    ordering = ('-payroll__week_end',)
    list_per_page = 50
    list_select_related = ('payroll', 'payroll__position', 'payroll__position__user')
    
    def get_week_end(self, obj):
        return obj.payroll.week_end
    get_week_end.short_description = 'Week End'
    get_week_end.admin_order_field = 'payroll__week_end'
    
    def get_position(self, obj):
        return obj.payroll.position
    get_position.short_description = 'Position'
    get_position.admin_order_field = 'payroll__position'

@admin.register(PayrollNotInHR)
class PayrollNotInHRAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'get_week_end', 'get_position')
    list_filter = ('payroll__status', 'payroll__week_end')
    search_fields = ('payroll__position__user__first_name', 'payroll__position__user__last_name')
    ordering = ('-payroll__week_end',)
    list_per_page = 50
    list_select_related = ('payroll', 'payroll__position', 'payroll__position__user')
    
    def get_week_end(self, obj):
        return obj.payroll.week_end
    get_week_end.short_description = 'Week End'
    get_week_end.admin_order_field = 'payroll__week_end'
    
    def get_position(self, obj):
        return obj.payroll.position
    get_position.short_description = 'Position'
    get_position.admin_order_field = 'payroll__position'
    
@admin.register(PayrollNotSigned)
class PayrollNotSignedAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'get_week_end', 'get_position')
    list_filter = ('payroll__status', 'payroll__week_end')
    search_fields = ('payroll__position__user__first_name', 'payroll__position__user__last_name')
    ordering = ('-payroll__week_end',)
    list_per_page = 50
    list_select_related = ('payroll', 'payroll__position', 'payroll__position__user')
    
    def get_week_end(self, obj):
        return obj.payroll.week_end
    get_week_end.short_description = 'Week End'
    get_week_end.admin_order_field = 'payroll__week_end'
    
    def get_position(self, obj):
        return obj.payroll.position
    get_position.short_description = 'Position'
    get_position.admin_order_field = 'payroll__position'
