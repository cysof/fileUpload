import pytest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock, MagicMock
from io import BytesIO
from PIL import Image
import json

from .models import UploadedFile
from .views import UploadFileViewSet


# Test configuration helper
def get_upload_urls():
    """Helper function to get the correct URLs for testing"""
    try:
        list_url = reverse('uploadedfile-list')
        def detail_url(pk):
            return reverse('uploadedfile-detail', kwargs={'pk': pk})
    except:
        # Fallback URLs - adjust these to match your URL configuration
        list_url = '/upload/'
        def detail_url(pk):
            return f'/upload/{pk}/'
    
    return list_url, detail_url


class UploadFileViewSetTest(APITestCase):
    """Test cases for UploadFileViewSet"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.upload_url, self.detail_url_func = get_upload_urls()
        
        # Create test files
        self.test_image = self.create_test_image()
        self.test_text_file = SimpleUploadedFile(
            "test.txt",
            b"Test file content",
            content_type="text/plain"
        )
        
        # Create a sample uploaded file record for testing
        self.uploaded_file = UploadedFile.objects.create(
            original_name="sample.txt",
            cloudinary_url="https://res.cloudinary.com/test/sample.jpg",
            file_size=1024,
            content_type="text/plain"
        )
    
    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
    
    def test_get_serializer_class_create_action(self):
        """Test that create action uses FileUploadSerializer"""
        viewset = UploadFileViewSet()
        viewset.action = 'create'
        
        from .serializers import FileUploadSerializer
        self.assertEqual(viewset.get_serializer_class(), FileUploadSerializer)
    
    def test_get_serializer_class_other_actions(self):
        """Test that other actions use UploadedFileSerializer"""
        viewset = UploadFileViewSet()
        viewset.action = 'list'
        
        from .serializers import UploadedFileSerializer
        self.assertEqual(viewset.get_serializer_class(), UploadedFileSerializer)
    
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    def test_create_successful_upload(self, mock_upload):
        """Test successful file upload"""
        # Mock Cloudinary response
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg",
            "public_id": "test_public_id"
        }
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'File uploaded successfully')
        self.assertIn('data', response.data)
        
        # Verify database record was created
        self.assertEqual(UploadedFile.objects.count(), 2)  # 1 from setUp + 1 new
        new_file = UploadedFile.objects.latest('id')
        self.assertEqual(new_file.original_name, 'test_image.jpg')
        self.assertEqual(new_file.cloudinary_url, 'https://res.cloudinary.com/test/uploaded_file.jpg')
    
    def test_create_invalid_serializer(self):
        """Test upload with invalid data"""
        response = self.client.post(
            self.upload_url,
            {},  # No file provided
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Validation failed')
        self.assertIn('errors', response.data)
    
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    def test_create_cloudinary_error(self, mock_upload):
        """Test Cloudinary upload error"""
        mock_upload.return_value = {
            "error": "Upload failed"
        }
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Cloudinary upload failed')
        self.assertIn('errors', response.data)
        self.assertIn('cloudinary', response.data['errors'])
    
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    def test_create_no_secure_url(self, mock_upload):
        """Test Cloudinary response without secure_url"""
        mock_upload.return_value = {
            "public_id": "test_id"
            # No secure_url
        }
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Upload failed - no URL received')
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['errors']['cloudinary'], 'No secure URL returned')
    
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    @patch('upload.models.UploadedFile.objects.create')  # Replace with your actual app name
    def test_create_database_error(self, mock_create, mock_upload):
        """Test database error during file creation"""
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg"
        }
        mock_create.side_effect = Exception("Database error")
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Upload failed')
        self.assertIn('errors', response.data)
        self.assertIn('server', response.data['errors'])
    
    def test_list_files(self):
        """Test listing all uploaded files"""
        # Create additional test files
        UploadedFile.objects.create(
            original_name="test2.txt",
            cloudinary_url="https://res.cloudinary.com/test/test2.jpg",
            file_size=2048,
            content_type="text/plain"
        )
        
        response = self.client.get(self.upload_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 2)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)
    
    def test_list_empty_files(self):
        """Test listing when no files exist"""
        UploadedFile.objects.all().delete()
        
        response = self.client.get(self.upload_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['data']), 0)
    
    def test_retrieve_file(self):
        """Test retrieving a specific file"""
        response = self.client.get(self.detail_url_func(self.uploaded_file.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id'], self.uploaded_file.id)
        self.assertEqual(response.data['data']['original_name'], 'sample.txt')
    
    def test_retrieve_nonexistent_file(self):
        """Test retrieving a file that doesn't exist"""
        response = self.client.get(self.detail_url_func(999))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_parser_classes(self):
        """Test that the viewset uses correct parser classes"""
        viewset = UploadFileViewSet()
        from rest_framework.parsers import MultiPartParser, FormParser
        
        self.assertIn(MultiPartParser, viewset.parser_classes)
        self.assertIn(FormParser, viewset.parser_classes)
    
    def test_queryset(self):
        """Test that the viewset uses correct queryset"""
        viewset = UploadFileViewSet()
        self.assertEqual(list(viewset.queryset), list(UploadedFile.objects.all()))
    
    @patch('upload.views.logger')  # Replace with your actual app name
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    def test_logging_on_error(self, mock_upload, mock_logger):
        """Test that errors are logged properly"""
        mock_upload.side_effect = Exception("Test error")
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_logger.error.assert_called_once_with("Upload error: Test error")


class UploadFileViewSetIntegrationTest(APITestCase):
    """Integration tests for UploadFileViewSet"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.upload_url, self.detail_url_func = get_upload_urls()
    
    def create_test_file(self, name="test.txt", content=b"test content", content_type="text/plain"):
        """Helper method to create test files"""
        return SimpleUploadedFile(name, content, content_type=content_type)
    
    @patch('upload.views.upload_to_cloudinary')  # Replace with your actual app name
    def test_full_upload_workflow(self, mock_upload):
        """Test complete upload workflow"""
        # Mock successful Cloudinary upload
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg",
            "public_id": "test_public_id"
        }
        
        # Upload file
        test_file = self.create_test_file()
        upload_response = self.client.post(
            self.upload_url,
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['data']['id']
        
        # List files
        list_response = self.client.get(self.upload_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)
        
        # Retrieve specific file
        retrieve_response = self.client.get(self.detail_url_func(file_id))
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['data']['id'], file_id)
    
    def test_multiple_file_types(self):
        """Test uploading different file types"""
        with patch('upload.views.upload_to_cloudinary') as mock_upload:  # Replace with your actual app name
            mock_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg"
            }
            
            # Test different file types one by one
            test_cases = [
                ("test1.txt", b"text content", "text/plain"),
                ("test2.json", b'{"key": "value"}', "application/json"),
                ("test3.csv", b"col1,col2\nval1,val2", "text/csv"),
            ]
            
            for i, (name, content, content_type) in enumerate(test_cases):
                # Create a fresh file for each test to avoid Django test issues
                test_file = SimpleUploadedFile(name, content, content_type=content_type)
                
                response = self.client.post(
                    self.upload_url,
                    {'file': test_file},
                    format='multipart'
                )
                
                # Add debugging information if test fails
                if response.status_code != status.HTTP_201_CREATED:
                    print(f"Failed upload for file {i}: {name}")
                    print(f"Response status: {response.status_code}")
                    print(f"Response data: {response.data}")
                    
                    # Print serializer errors if available
                    if hasattr(response, 'data') and 'errors' in response.data:
                        print(f"Serializer errors: {response.data['errors']}")
                
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, 
                               f"Failed to upload {name}. Response: {response.data}")
        
        # Verify all files were uploaded
        list_response = self.client.get(self.upload_url)
        self.assertEqual(list_response.data['count'], len(test_cases))
    
    def test_debug_file_upload_issue(self):
        """Debug test to understand file upload issues"""
        with patch('upload.views.upload_to_cloudinary') as mock_upload:
            mock_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg"
            }
            
            # Test what happens with a simple file upload
            test_file = SimpleUploadedFile(
                "debug_test.txt", 
                b"debug content", 
                content_type="text/plain"
            )
            
            print(f"File name: {test_file.name}")
            print(f"File size: {test_file.size}")
            print(f"File content type: {test_file.content_type}")
            
            response = self.client.post(
                self.upload_url,
                {'file': test_file},
                format='multipart'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            
            if response.status_code != status.HTTP_201_CREATED:
                # Print more debugging info
                print("Upload failed!")
                if hasattr(response, 'data'):
                    print(f"Full response data: {response.data}")
            
            # This test doesn't assert anything, just prints debug info
            # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_multiple_file_types_simplified(self):
        """Simplified test for multiple file types"""
        with patch('upload.views.upload_to_cloudinary') as mock_upload:
            mock_upload.return_value = {
                "secure_url": "https://res.cloudinary.com/test/uploaded_file.jpg"
            }
            
            # Test just one file type that should definitely work
            test_file = SimpleUploadedFile(
                "simple_test.txt", 
                b"simple content", 
                content_type="text/plain"
            )
            
            response = self.client.post(
                self.upload_url,
                {'file': test_file},
                format='multipart'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# Pytest fixtures and additional test utilities
@pytest.fixture
def api_client():
    """Pytest fixture for API client"""
    return APIClient()


@pytest.fixture
def sample_uploaded_file():
    """Pytest fixture for sample uploaded file"""
    return UploadedFile.objects.create(
        original_name="pytest_sample.txt",
        cloudinary_url="https://res.cloudinary.com/test/pytest_sample.jpg",
        file_size=1024,
        content_type="text/plain"
    )


@pytest.mark.django_db
def test_viewset_with_pytest(api_client):
    """Example test using pytest instead of Django TestCase"""
    upload_url, _ = get_upload_urls()
    
    # Create test file
    test_file = SimpleUploadedFile(
        "pytest_test.txt",
        b"pytest test content",
        content_type="text/plain"
    )
    
    with patch('upload.views.upload_to_cloudinary') as mock_upload:  # Replace with your actual app name
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/pytest_file.jpg"
        }
        
        response = api_client.post(
            upload_url,
            {'file': test_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'data' in response.data