from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadedFile

class FileUploadTests(APITestCase):
    def test_upload_valid_file(self):
        """
        Tests that a valid file can be uploaded to Cloudinary and a corresponding
        UploadedFile object is created in the database.

        The test sends a POST request to the file-upload endpoint with a valid
        file, and checks that a 201 Created response is returned, with the
        cloudinary_url key included in the response data. It also checks that
        only one UploadedFile object has been created in the database.
        """
        url = reverse("file-upload")
        file_data = SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
        response = self.client.post(url, {"file": file_data})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("cloudinary_url", response.data)
        self.assertEqual(UploadedFile.objects.count(), 1)

    def test_upload_large_file(self):
        """
        Tests that a file that exceeds the 10MB limit is rejected with a 400
        Bad Request response, and that the response data contains an error
        message for the file field.
        """
        url = reverse("file-upload")
        large_content = b"x" * (10 * 1024 * 1024 + 1)
        file_data = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")
        response = self.client.post(url, {"file": file_data})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)
    
    def test_upload_without_file(self):
        """
        Tests that an attempt to upload without providing a file returns a 400
        Bad Request response.

        The test sends a POST request to the file-upload endpoint without any
        file data and checks that the response status code is 400 Bad Request.
        """

        url = reverse("file-upload")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)