# models.py
from django.db import models
from django.utils import timezone


class UploadedFile(models.Model):
    original_name = models.CharField(max_length=255)
    cloudinary_url = models.URLField(max_length=500)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    content_type = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'
    
    def __str__(self):
        return f"{self.original_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None