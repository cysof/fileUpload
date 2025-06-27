# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'original_name',
        'file_size_display',
        'content_type',
        'preview_link',
        'download_link',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'content_type',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'original_name',
        'content_type'
    ]
    
    readonly_fields = [
        'id',
        'file_size_display',
        'file_size_mb_display',
        'preview_image',
        'cloudinary_preview',
        'created_at',
        'updated_at'
    ]
    
    fields = [
        'id',
        'original_name',
        'cloudinary_url',
        'cloudinary_preview',
        'preview_image',
        'file_size',
        'file_size_display',
        'file_size_mb_display',
        'content_type',
        'created_at',
        'updated_at'
    ]
    
    ordering = ['-created_at']
    
    list_per_page = 25
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} bytes"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "Unknown"
    file_size_display.short_description = "File Size"
    
    def file_size_mb_display(self, obj):
        """Display file size in MB"""
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "Unknown"
    file_size_mb_display.short_description = "Size (MB)"
    
    def preview_link(self, obj):
        """Create a preview link for the file"""
        if obj.cloudinary_url:
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview</a>',
                obj.cloudinary_url
            )
        return "No URL"
    preview_link.short_description = "Preview"
    
    def download_link(self, obj):
        """Create a download link for the file"""
        if obj.cloudinary_url:
            # For Cloudinary URLs, you can add fl_attachment to force download
            download_url = obj.cloudinary_url.replace('/upload/', '/upload/fl_attachment/')
            return format_html(
                '<a href="{}" target="_blank" class="button">Download</a>',
                download_url
            )
        return "No URL"
    download_link.short_description = "Download"
    
    def preview_image(self, obj):
        """Show image preview if the file is an image"""
        if obj.cloudinary_url and obj.content_type and obj.content_type.startswith('image/'):
            # Create a thumbnail version using Cloudinary transformations
            thumbnail_url = obj.cloudinary_url.replace(
                '/upload/', 
                '/upload/w_200,h_200,c_fit,q_auto/'
            )
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd;" />',
                thumbnail_url
            )
        return "Not an image"
    preview_image.short_description = "Image Preview"
    
    def cloudinary_preview(self, obj):
        """Show Cloudinary URL with copy button"""
        if obj.cloudinary_url:
            return format_html(
                '''
                <div style="max-width: 400px;">
                    <input type="text" value="{}" readonly 
                           style="width: 100%; margin-bottom: 5px;" 
                           onclick="this.select();" />
                    <br>
                    <small>Click to select and copy</small>
                </div>
                ''',
                obj.cloudinary_url
            )
        return "No URL"
    cloudinary_preview.short_description = "Cloudinary URL"
    
    def get_queryset(self, request):
        """Optimize queryset to avoid N+1 queries"""
        queryset = super().get_queryset(request)
        return queryset.select_related()
    
    def has_add_permission(self, request):
        """Disable adding files through admin (use API instead)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but limit editing"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion through admin"""
        return True
    
    class Media:
        css = {
            'all': ('admin/css/custom_file_admin.css',)
        }
        js = ('admin/js/custom_file_admin.js',)


# Optional: Custom admin action to bulk delete files
def bulk_delete_files(modeladmin, request, queryset):
    """Custom admin action to bulk delete files"""
    count = queryset.count()
    
    # Optional: Add Cloudinary cleanup here
    # for file_obj in queryset:
    #     try:
    #         delete_from_cloudinary(file_obj.cloudinary_url)
    #     except Exception as e:
    #         messages.warning(request, f"Failed to delete {file_obj.original_name} from Cloudinary: {e}")
    
    queryset.delete()
    
    modeladmin.message_user(
        request,
        f"Successfully deleted {count} file(s)."
    )

bulk_delete_files.short_description = "Delete selected files"

# Add the custom action to the admin
UploadedFileAdmin.actions = [bulk_delete_files]


# Optional: Create a custom admin site title
admin.site.site_header = "File Upload Management"
admin.site.site_title = "File Admin"
admin.site.index_title = "Welcome to File Upload Administration"