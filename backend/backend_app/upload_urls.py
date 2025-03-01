from django.urls import path
from .views import upload_video, store_link, ensure_playlist, check_task_status

urlpatterns = [
    # Video Upload
    path("video/", upload_video, name="upload_video"),
    #Video Linking
    path("link/", store_link, name="store_link"),
    #Playlist Checking
    path("playlist/", ensure_playlist, name="ensure_playlist"),
    # Task Status
    path("status/<str:task_id>/", check_task_status, name="check_task_status")
]