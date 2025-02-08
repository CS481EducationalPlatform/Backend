from django.urls import path
from .views import upload_video

urlpatterns = [
    path("video/", upload_video, name="upload_video"),
]