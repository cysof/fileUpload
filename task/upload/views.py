from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import UploadedFile
from .serializers import FileUploadSerializer, UploadedFileSerializer
from .utils import upload_to_cloudinary
import logging

logger = logging.getLogger(__name__)


class UploadFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]  # Important for file uploads
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FileUploadSerializer
        return UploadedFileSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle file upload"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        
        try:
            # Upload to Cloudinary
            result = upload_to_cloudinary(file)
            
            if result.get("error"):
                return Response({
                    'success': False,
                    'message': 'Cloudinary upload failed',
                    'errors': {'cloudinary': result.get('error')}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if "secure_url" not in result:
                return Response({
                    'success': False,
                    'message': 'Upload failed - no URL received',
                    'errors': {'cloudinary': 'No secure URL returned'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create database record
            uploaded_file = UploadedFile.objects.create(
                original_name=file.name,
                cloudinary_url=result["secure_url"],
                file_size=file.size,
                content_type=file.content_type,
            )
            
            # Return success response
            response_serializer = UploadedFileSerializer(uploaded_file)
            return Response({
                'success': True,
                'message': 'File uploaded successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Upload failed',
                'errors': {'server': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """List all uploaded files"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': len(serializer.data),
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific uploaded file"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })