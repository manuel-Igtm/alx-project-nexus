from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BlockedIP, AllowedIP, IPAccessLog, LoginAttempt, SecurityAlert


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'blocked_at', 'expires_at', 'is_permanent', 'status_badge']
    list_filter = ['reason', 'is_permanent', 'blocked_at']
    search_fields = ['ip_address', 'description']
    readonly_fields = ['blocked_at']
    date_hierarchy = 'blocked_at'
    
    fieldsets = (
        ('IP Information', {
            'fields': ('ip_address', 'reason', 'description')
        }),
        ('Block Settings', {
            'fields': ('is_permanent', 'expires_at', 'blocked_by')
        }),
        ('Timestamps', {
            'fields': ('blocked_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: red; font-weight: bold;">🔒 Active</span>')
        return format_html('<span style="color: green;">✓ Expired</span>')
    status_badge.short_description = 'Status'
    
    actions = ['unblock_ips', 'make_permanent']
    
    def unblock_ips(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"Unblocked {queryset.count()} IP addresses.")
    unblock_ips.short_description = "Unblock selected IPs"
    
    def make_permanent(self, request, queryset):
        queryset.update(is_permanent=True, expires_at=None)
        self.message_user(request, f"Made {queryset.count()} blocks permanent.")
    make_permanent.short_description = "Make blocks permanent"


@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'description', 'created_at', 'created_by']
    search_fields = ['ip_address', 'description']
    readonly_fields = ['created_at']


@admin.register(IPAccessLog)
class IPAccessLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'endpoint', 'method', 'status_code', 'response_time_ms', 'is_suspicious', 'timestamp']
    list_filter = ['method', 'is_suspicious', 'status_code', 'timestamp']
    search_fields = ['ip_address', 'endpoint', 'user_agent']
    readonly_fields = ['ip_address', 'user', 'endpoint', 'method', 'status_code', 'user_agent', 
                       'request_data', 'response_time_ms', 'timestamp', 'country', 'city', 
                       'is_suspicious', 'threat_score']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'email', 'was_successful', 'timestamp', 'status_icon']
    list_filter = ['was_successful', 'timestamp']
    search_fields = ['ip_address', 'email']
    readonly_fields = ['ip_address', 'email', 'was_successful', 'timestamp', 'user_agent']
    date_hierarchy = 'timestamp'
    
    def status_icon(self, obj):
        if obj.was_successful:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    status_icon.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity_badge', 'ip_address', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_resolved', 'created_at']
    search_fields = ['title', 'description', 'ip_address']
    readonly_fields = ['ip_address', 'user', 'alert_type', 'title', 'description', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('title', 'alert_type', 'severity', 'description')
        }),
        ('Source', {
            'fields': ('ip_address', 'user')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def severity_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f"Marked {queryset.count()} alerts as resolved.")
    mark_resolved.short_description = "Mark as resolved"
