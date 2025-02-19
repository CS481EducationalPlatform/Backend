import logging
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from celery.result import AsyncResult

from rest_framework import viewsets

from .tasks import upload_to_youtube
from .models import UserInfo, Topics, Tags, Courses, Lessons, AppliedTags, AppliedTopics, Uploaded
from .serializers import UserInfoSerializer, TopicSerializer, TagSerializer, CourseSerializer, LessonSerializer, AppliedTagSerializer, AppliedTopicSerializer, UploadedSerializer

logger = logging.getLogger("django")

#View Task Status
def get_task_status(request, task_id):
    logger.debug("Task Status Requested")
    task_result = AsyncResult(task_id)
    logger.debug(f"Task Result: {task_result}")
    response_data = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }
    return JsonResponse(response_data)

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
            user_id = request.POST.get("user_id")
            course_id = request.POST.get("course_id")
            access_token = request.POST.get("accessToken")

            #Ensure file
            if not file:
                return JsonResponse({"error": "File is required"}, status=400)

            # Log received data
            logger.debug(f"Received title: {title}, description: {description}")
            logger.debug(f"User: {user_id}, Course: {course_id}")
            logger.debug(f"Access Token: {access_token}")
            logger.debug(f"Received file: {file.name} (Size: {file.size} bytes)")

            #Read file and encode to base64 for transfer
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode()

            logger.debug("Attempting YT Video Enqueue")
            #At a delay (queue with Celery/Redis for task based) call upload
            task = upload_to_youtube.delay(
                file_base64,
                file.size,
                title,
                description,
                access_token,
            )  # Enqueue Celery task with required information
            logger.debug("YouTube video queued")

            return JsonResponse({"message": "File uploaded successfully", "filename": file.name, "task_id":task.id}, status=200,)
        else:
            return JsonResponse({"error": "Invalid Content-Type"}, status=400)
    except Exception as e:
        logger.error(f"Upload attempted but failed: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)

class UserInfoViewAll(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

class TopicViewAll(viewsets.ModelViewSet):
    queryset = Topics.objects.all()
    serializer_class = TopicSerializer

class TagViewAll(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer

class CourseViewAll(viewsets.ModelViewSet):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer

class LessonViewAll(viewsets.ModelViewSet):
    queryset = Lessons.objects.all()
    serializer_class = LessonSerializer

class AppliedTagViewAll(viewsets.ModelViewSet):
    queryset = AppliedTags.objects.all()
    serializer_class = AppliedTagSerializer

class AppliedTopicViewAll(viewsets.ModelViewSet):
    queryset = AppliedTopics.objects.all()
    serializer_class = AppliedTopicSerializer

class UploadedViewAll(viewsets.ModelViewSet):
    queryset = Uploaded.objects.all()
    serializer_class = UploadedSerializer
