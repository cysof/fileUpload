# Django File Upload API with Cloudinary Integration

A robust Django REST Framework application for handling file uploads with Cloudinary cloud storage integration. This project provides a complete file management solution with both API endpoints and admin interface for seamless file operations.

## 🚀 Features

### Core Functionality
- **Secure File Upload**: Upload files through REST API endpoints
- **Cloud Storage**: Automatic file storage using Cloudinary
- **File Validation**: Size, type, and security validation
- **Metadata Tracking**: Complete file information storage
- **RESTful API**: Full CRUD operations for file management

### API Features
- **Multiple Upload Formats**: Support for various file types (images, documents, PDFs)
- **File Size Validation**: Configurable file size limits (default: 10MB)
- **Content Type Validation**: Whitelist-based file type security
- **Standardized Responses**: Consistent JSON response format
- **Error Handling**: Comprehensive error messages and logging
- **Browsable API**: Django REST Framework's interactive API interface

### Admin Interface Features
- **Rich File Management**: Enhanced Django admin for file operations
- **Image Previews**: Thumbnail previews for uploaded images
- **File Information Display**: Size, type, upload date, and metadata
- **Quick Actions**: Preview, download, and copy URL functionality
- **Search & Filter**: Find files by name, type, or upload date
- **Bulk Operations**: Delete multiple files simultaneously
- **Responsive Design**: Mobile-friendly admin interface

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+
- Cloudinary Python SDK
- Pillow (for image processing)

## 🛠 Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd django-file-upload-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt


### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## 🔧 Configuration

### Cloudinary Setup
1. Create a free account at [Cloudinary](https://cloudinary.com/)
2. Get your cloud name, API key, and API secret from the dashboard
3. Add these credentials to your `.env` file

### File Upload Settings
Configure in `settings.py`:
```python
# Maximum file size (adjust as needed)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# Allowed file types (modify in serializers.py)
ALLOWED_FILE_TYPES = [
    'image/jpeg', 'image/png', 'image/gif',
    'application/pdf', 'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/upload/
```

### Endpoints

#### 1. Upload File
**POST** `/file-uploads/`

Upload a new file to Cloudinary and save metadata.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload/file-uploads/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "id": 1,
    "original_name": "example.jpg",
    "cloudinary_url": "https://res.cloudinary.com/...",
    "file_size": 245760,
    "file_size_mb": 0.23,
    "content_type": "image/jpeg",
    "upload_date": "2025-06-27T10:30:00Z"
  }
}
```

#### 2. List All Files
**GET** `/file-uploads/`

Retrieve all uploaded files with metadata.

**Response:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": 1,
      "original_name": "document.pdf",
      "cloudinary_url": "https://res.cloudinary.com/...",
      "file_size": 1048576,
      "file_size_mb": 1.0,
      "content_type": "application/pdf",
      "upload_date": "2025-06-27T10:30:00Z"
    }
  ]
}
```

#### 3. Get Specific File
**GET** `/file-uploads/{id}/`

Retrieve details of a specific uploaded file.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "original_name": "presentation.pptx",
    "cloudinary_url": "https://res.cloudinary.com/...",
    "file_size": 2097152,
    "file_size_mb": 2.0,
    "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "upload_date": "2025-06-27T10:30:00Z"
  }
}
```

#### 4. Delete File
**DELETE** `/file-uploads/{id}/`

Delete a file record from database (Cloudinary file remains).

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### Error Responses

#### Validation Error
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "file": ["File size cannot exceed 10MB"]
  }
}
```

#### Upload Error
```json
{
  "success": false,
  "message": "Cloudinary upload failed",
  "errors": {
    "cloudinary": "Invalid file format"
  }
}
```

## 🎛 Admin Interface

### Accessing Admin
1. Create superuser: `python manage.py createsuperuser`
2. Visit: `http://localhost:8000/admin/`
3. Navigate to "Uploaded Files" section

### Admin Features

#### File Management Dashboard
- **List View**: Overview of all uploaded files with key information
- **Pagination**: 25 files per page for optimal performance
- **Search Bar**: Search by filename or content type
- **Filters**: Filter by content type, upload date

#### File Details View
- **Image Previews**: Automatic thumbnails for image files
- **File Information**: Size, type, upload date, and metadata
- **URL Management**: Easy copy-to-clipboard for Cloudinary URLs
- **Quick Actions**: Preview and download buttons

#### Enhanced Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Hover Previews**: Image preview on mouse hover
- **Copy Functionality**: One-click URL copying
- **Bulk Actions**: Delete multiple files at once
- **File Size Display**: Human-readable file sizes (KB, MB)
- **Content Type Badges**: Color-coded file type indicators

#### Admin Permissions
- **View Only**: Files cannot be uploaded through admin
- **Delete Access**: Remove files and records
- **Search & Filter**: Find specific files quickly
- **Bulk Operations**: Manage multiple files simultaneously

## 🔒 Security Features

### File Validation
- **Size Limits**: Configurable maximum file size (default: 10MB)
- **Type Validation**: Whitelist of allowed file types
- **Content Verification**: MIME type checking
- **Malicious File Detection**: Basic security scanning

### API Security
- **CSRF Protection**: Built-in Django CSRF protection
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error messages without sensitive data
- **Rate Limiting**: Configurable upload rate limits

### Cloudinary Security
- **Secure URLs**: HTTPS-only file access
- **Access Control**: Private uploads with signed URLs
- **Automatic Optimization**: Image optimization and compression
- **CDN Delivery**: Fast, secure file delivery

## 🚀 Usage Examples

### Frontend Integration

#### JavaScript/Fetch API
```javascript
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/upload/file-uploads/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'), // If CSRF enabled
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Upload successful:', result.data);
      return result.data;
    } else {
      console.error('Upload failed:', result.errors);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

#### React Component
```jsx
import React, { useState } from 'react';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('/api/upload/file-uploads/', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={(e) => setFile(e.target.files[0])} 
      />
      <button 
        onClick={handleUpload} 
        disabled={!file || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload File'}
      </button>
      
      {result && (
        <div>
          {result.success ? (
            <p>✅ Upload successful! 
               <a href={result.data.cloudinary_url} target="_blank">
                 View File
               </a>
            </p>
          ) : (
            <p>❌ Upload failed: {result.message}</p>
          )}
        </div>
      )}
    </div>
  );
};
```

### Python/Django Integration
```python
import requests

def upload_file_to_api(file_path):
    url = 'http://localhost:8000/api/upload/file-uploads/'
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        
        if response.status_code == 201:
            data = response.json()
            print(f"Upload successful: {data['data']['cloudinary_url']}")
            return data['data']
        else:
            print(f"Upload failed: {response.json()}")
            return None
```

## 🔧 Customization

### Adding New File Types
Edit `serializers.py`:
```python
allowed_types = [
    'image/jpeg', 'image/png', 'image/gif',
    'application/pdf',
    'text/plain',
    'video/mp4',  # Add video support
    'audio/mpeg', # Add audio support
]
```

### Modifying File Size Limits
Edit `serializers.py`:
```python
def validate_file(self, value):
    max_size = 50 * 1024 * 1024  # 50MB limit
    if value.size > max_size:
        raise serializers.ValidationError("File size cannot exceed 50MB")
```

### Custom Admin Actions
Add to `admin.py`:
```python
def export_file_list(modeladmin, request, queryset):
    # Custom export functionality
    pass

export_file_list.short_description = "Export file list"
UploadedFileAdmin.actions.append(export_file_list)
```

## 🐛 Troubleshooting

### Common Issues

#### Upload Not Working
1. Check Cloudinary credentials in `.env`
2. Verify file size limits
3. Ensure file type is allowed
4. Check server logs for detailed errors

#### Admin Interface Issues
1. Run `python manage.py collectstatic`
2. Check static files configuration
3. Verify admin user permissions

#### API 400 Errors
1. Check request format (multipart/form-data)
2. Verify file field name is 'file'
3. Check CSRF token if protection enabled

### Debug Mode
Enable detailed logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'upload.log',
        },
    },
    'loggers': {
        'your_app': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 📈 Performance Optimization

### File Upload Optimization
- **Async Processing**: Use Celery for large file processing
- **Chunked Uploads**: Implement chunked upload for large files
- **Compression**: Enable Cloudinary auto-optimization
- **CDN**: Leverage Cloudinary's global CDN

### Database Optimization
- **Indexing**: Add database indexes for frequently searched fields
- **Pagination**: Implement pagination for large file lists
- **Caching**: Use Redis/Memcached for file metadata

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Django REST Framework](https://www.django-rest-framework.org/) for the excellent API framework
- [Cloudinary](https://cloudinary.com/) for cloud storage and image optimization
- [Django](https://www.djangoproject.com/) for the robust web framework

## 📞 Support

For support, please open an issue on GitHub or contact [your-email@example.com].

---

**Built with ❤️ using Django REST Framework and Cloudinary**