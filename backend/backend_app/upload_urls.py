from django.urls import path
from .views import upload_video, get_task_status

urlpatterns = [
    # Video Upload
    path("video/", upload_video, name="upload_video"),
    # Task Status
    path("status/<str:task_id>/", get_task_status, name="get_task_status")
]