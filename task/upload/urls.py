from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadFileViewSet

router = DefaultRouter()
router.register(r'file-uploads', UploadFileViewSet)

urlpatterns = [
    path('upload/', include(router.urls)),
]