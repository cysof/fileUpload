# upload/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
import tempfile
from PIL import Image
import io
import responses
from urllib.parse import urlparse

class FileUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @responses.activate
    @patch('upload.utils.upload_to_cloudinary')
    def test_upload_valid_file(self, mock_upload):
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/dmlrvkbnp/image/upload/v1750978613/cgacm09johm17wzx42fz.png'
        }

        # Create a valid image file
        image = Image.new('RGB', (100, 100))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        response = self.client.post('/api/upload/', {'file': image_bytes}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cloudinary_url', response.data)

        # Check if the cloudinary_url is a valid URL
        cloudinary_url = response.data['cloudinary_url']
        parsed_url = urlparse(cloudinary_url)
        self.assertEqual(parsed_url.scheme, 'https')
        self.assertEqual(parsed_url.netloc, 'res.cloudinary.com')
        self.assertIn('image/upload', parsed_url.path)