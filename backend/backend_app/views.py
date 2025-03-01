import logging
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets

from celery.result import AsyncResult

from .tasks import link_uploaded, upload_to_youtube, ensure_playlist_exists
from .models import (
    UserInfo, Instructor, Topics, Courses, Lessons, Rating, Tags, 
    TopicTag, CourseTag, LessonTag, Uploaded
)
from .serializers import (
    UserInfoSerializer, InstructorSerializer, TopicSerializer, 
    CourseSerializer, LessonSerializer, RatingSerializer, 
    TagSerializer, TopicTagSerializer, CourseTagSerializer, 
    LessonTagSerializer, UploadedSerializer
)

logger = logging.getLogger("django")

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def check_task_status(request, task_id):
    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse({"status": "completed", "result": result.result})
    return JsonResponse({"status": "pending"})

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def ensure_playlist(request):
    logger.debug("Attempting playlist ensure")

    if(request.method != "POST"):
        return JsonResponse({"error":"Only POST allowed"}, status=405)
    
    try:
        if request.content_type.startswith("multipart/form-data"):
            playlist_name = request.POST.get("playlist_name")
            access_token = request.POST.get("access_token")
            
            task_result = ensure_playlist_exists.delay(
                playlist_name,
                access_token
            )
            logger.debug(f"PLAYLIST TASK ID: {task_result.id}")

            return JsonResponse({f"task_id":task_result.id}, status=202)
    except Exception as e:
        logger.error(f"Playlist Ensure attempted but failed: {e}")
        return JsonResponse({"error": "Internal Server Error in Playlist Ensure"}, status=500)

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def store_link(request):
    logger.debug("Attempting video link")

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        if request.content_type.startswith("multipart/form-data"):
            lesson_id = request.POST.get("lesson_id")
            video_url = request.POST.get("video_url")
            link = link_uploaded.delay(
                int(lesson_id),
                video_url
            )
            logger.debug(f"LINKED : {video_url}")
            if(link == 0):
                return JsonResponse({"message": "Video linked successfully", "video_url":video_url}, status=200,)
            else:
                return JsonResponse({"message": "Video linking failure"}, status=500)
        else:
            return JsonResponse({"error": "Invalid Content-Type"}, status=400)
    except Exception as e:
        logger.error(f"Linking attempted but failed: {e}")
        return JsonResponse({"error": "Internal Server Error in Linking"}, status=500)

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def upload_video(request):
    logger.debug("Attempting video upload")

    #Ensure POST is used to give data to backend
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
       # Ensure it's a file upload request that can hold a file as JSON will not
        if request.content_type.startswith("multipart/form-data"):
            logger.debug("Processing multipart/form-data request")

            #Parse information
            file = request.FILES.get("file")
            title = request.POST.get("title")
            description = request.POST.get("description")
            lesson_id = request.POST.get("lesson_id")
            playlist = request.POST.get("playlist")
            access_token = request.POST.get("accessToken")

            #Ensure file
            if not file:
                return JsonResponse({"error": "File is required"}, status=400)

            # Log received data
            logger.debug(f"Received title: {title}, description: {description}")
            logger.debug(f"Access Token: {access_token}")
            logger.debug(f"Received file: {file.name} (Size: {file.size} bytes)")

            #Read file and encode to base64 for transfer
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode()

            logger.debug("Attempting YT Video Enqueue")
            #At a delay (queue with Celery/Redis for task based) call upload
            upload_res = upload_to_youtube.delay(
                file_base64,
                file.size,
                title,
                description,
                access_token,
                lesson_id,
                playlist
            )  # Enqueue Celery task with required information
            logger.debug("YouTube video queued")

            if(upload_res == 0):
                return JsonResponse({"message": "File uploaded successfully", "filename": file.name}, status=200,)
            else:
                return JsonResponse({"message": "File upload failure"}, status=500)
        else:
            return JsonResponse({"error": "Invalid Content-Type"}, status=400)
    except Exception as e:
        logger.error(f"Upload attempted but failed: {e}")
        return JsonResponse({"error": "Internal Server Error in Upload"}, status=500)

class UserInfoViewAll(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

class InstructorViewAll(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

class TopicViewAll(viewsets.ModelViewSet):
    queryset = Topics.objects.all()
    serializer_class = TopicSerializer

class CourseViewAll(viewsets.ModelViewSet):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer

class LessonViewAll(viewsets.ModelViewSet):
    queryset = Lessons.objects.all()
    serializer_class = LessonSerializer

class RatingViewAll(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class TagViewAll(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer

class TopicTagViewAll(viewsets.ModelViewSet):
    queryset = TopicTag.objects.all()
    serializer_class = TopicTagSerializer

class CourseTagViewAll(viewsets.ModelViewSet):
    queryset = CourseTag.objects.all()
    serializer_class = CourseTagSerializer

class LessonTagViewAll(viewsets.ModelViewSet):
    queryset = LessonTag.objects.all()
    serializer_class = LessonTagSerializer

class UploadedViewAll(viewsets.ModelViewSet):
    queryset = Uploaded.objects.all()
    serializer_class = UploadedSerializer
