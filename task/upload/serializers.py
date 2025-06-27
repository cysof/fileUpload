from rest_framework import serializers
from .models import UploadedFile


class FileUploadSerializer(serializers.Serializer):
    """
    Serializer for handling file uploads
    """
    file = serializers.FileField(
        required=True,
        help_text="Select a file to upload",
        style={'template': 'rest_framework/input/file.html'}
    )
    
    def validate_file(self, value):
        """
        Validate the uploaded file
        """
        # File size validation (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # File type validation
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'application/pdf', 'text/plain', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"File type '{value.content_type}' is not supported. "
                f"Allowed types: {', '.join(allowed_types)}"
            )
        
        return value


class UploadedFileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying uploaded file information
    """
    file_size_mb = serializers.SerializerMethodField()
    upload_date = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = UploadedFile
        fields = [
            'id', 
            'original_name', 
            'cloudinary_url', 
            'file_size',
            'file_size_mb',
            'content_type',
            'upload_date'
        ]
        read_only_fields = ['id', 'cloudinary_url', 'upload_date']
    
    def get_file_size_mb(self, obj):
        """
        Convert file size to MB for better readability
        """
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class FileUploadResponseSerializer(serializers.Serializer):
    """
    Serializer for standardized API responses
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = UploadedFileSerializer(required=False)
    errors = serializers.DictField(required=False)