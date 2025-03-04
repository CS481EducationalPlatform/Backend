from django.urls import path
from .views import get_youtube_videos, delete_youtube_video, update_youtube_video, check_task_status

urlpatterns = [
    #Get Videos
    path("videos/", get_youtube_videos, name="get_youtube_videos"),
    #Modify Video
    path("delete/", delete_youtube_video, name="delete_youtube_video"),
    #Delete Video
    path("update/", update_youtube_video, name="update_youtube_video"),
    # Task Status
    path("status/<str:task_id>/", check_task_status, name="check_task_status")
]