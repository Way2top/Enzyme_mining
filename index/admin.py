from django.contrib import admin
from .models import FastaFile, VisitLog

@admin.register(FastaFile)
class FastaFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'file_path', 'upload_date')
    search_fields = ('name', 'description')
    list_filter = ('upload_date',)

@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'visit_time', 'viewed_file', 'operation_type', 'page_url', 'request_data')
    list_filter = ('visit_time', 'viewed_file', 'operation_type')
    search_fields = ('ip_address', 'user_agent', 'page_url', 'request_data')
    readonly_fields = ('ip_address', 'user_agent', 'visit_time', 'viewed_file', 'operation_type', 'page_url', 'request_data')
