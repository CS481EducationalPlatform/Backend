import json
import logging
import base64
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

#Helper function to prevent bad logging from causing actual failures
def log(print_string):
    try : logger.debug(print_string) 
    except : logger.debug("Log_Fail_Caught")

#Helper function to remove OAuth from Authorization Header
def extract_token_from_header(request):
    log(f"Called_Extract_Token_From_Header : {request}")
    auth_header = request.headers.get('Authorization', '')
    log(f"Auth_Header_Extract: {auth_header}")
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    #Depending on request format might also be within body data
    try:
        body_data = json.loads(request.body)
        if isinstance(body_data, dict) and 'data' in body_data:
            data_str = body_data['data']
            data_obj = json.loads(data_str)
            if 'headers' in data_obj and 'Authorization' in data_obj['headers']:
                auth = data_obj['headers']['Authorization']
                if auth.startswith('Bearer '):
                    return auth[7:]
    except:
        pass
    return None

#Helper function to remove youtube junk from youtube id in url
def extract_video_id(youtube_url):
    log(f"Called_Extract_Video_Id")
    #Patterns Generated with Claude 3.7 Sonnet
    patterns=[
        r'(?:youtube\.com\/watch\?v=|youtu.be\/)([^&\n?]+)',
        r'youtube\.com\/shorts\/([^&\n?]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            log(f"Video_Match_Extract : {match.group(1)}")
            return match.group(1)
    log(f"ID_Not_Extracted")
    return None

def fetch_video_details(access_token, video_ids):
    log(f"Called_Fetch_Video_Details")
    # Set up API request fields
    video_ids_str = ",".join(video_ids)
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails,statistics,status",
        "id": video_ids_str
    }
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    #Make API Request
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return []

    data = response.json()
    videos = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})
        statistics = item.get("statistics", {})
        status = item.get("status", {})
        tags = snippet.get("tags", [])

        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = None
        for quality in ["maxres", "standard", "high", "medium", "default"]:
            if quality in thumbnails:
                thumbnail_url = thumbnails[quality].get('url')
                break

        # Made with AI
        video = {
            "id": item.get("id"),
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "youtube_url": f"https://www.youtube.com/watch?v={item.get('id')}",
            "thumbnail_url": thumbnail_url,
            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "tags": tags,
            "category_id": snippet.get("categoryId"),
            "duration": content_details.get("duration"),
            "view_count": statistics.get("viewCount", 0),
            "like_count": statistics.get("likeCount", 0),
            "comment_count": statistics.get("commentCount", 0),
            "privacy_status": status.get("privacyStatus"),
            "embeddable": status.get("embeddable", True),
            "license": status.get("license"),
        }

        videos.append(video)
    log(f"Videos_Fetched : {videos}")
    return videos

def fetch_youtube_videos(access_token, max_results= 50):
    log(f"Called_Fetch_Youtube_Videos")
    videos = []
    next_page_token = None
    
    try:
        while True:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "forMine": "true",
                "type": "video",
                "maxResults": max_results
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }

            response = requests.get(url, params=params, headers=headers)
            log(f"Fetch_Youtube_Videos_Response : {response}")

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown Error")
                    # Check specifically for token expiration
                    if response.status_code == 401:
                        return {
                            "success": False,
                            "error": "Token expired",
                            "error_code": "TOKEN_EXPIRED",
                            "details": error_message
                        }
                    return {"success": False, "error": error_message}
                except ValueError:
                    return {"success": False, "error": f"HTTP Error: {response.status_code}"}
                
            data = response.json()

            video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
            if video_ids:
                detailed_videos = fetch_video_details(access_token, video_ids)
                videos.extend(detailed_videos)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        return {"success": True, "videos": videos}
    except Exception as e:
        return {"success": False, "error": str(e)}

@csrf_exempt
@require_GET
def get_youtube_videos(request):
    log(f"Called_Get_Youtube_Videos")

    try:
        access_token = extract_token_from_header(request)
        if not access_token:
            return JsonResponse({
                "success": False,
                "error": "No Auth Token Provided Currently"
            }, status=401)

        result = fetch_youtube_videos(access_token)

        if result["success"]:
            return JsonResponse({"success": True, "videos": result["videos"]})
        else:
            return JsonResponse({"success": False, "error": result["error"]}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@require_POST
def update_youtube_video(request):
    log(f"Called_Update_Youtube_Video")
    try:
        access_token = extract_token_from_header(request)
        if not access_token:
            return JsonResponse({
                "success": False,
                "error": "No Auth Token Provided"
            }, status=401)
        
        data = json.loads(request.body)
        youtube_url = data.get("youtube_url")
        if not youtube_url:
            return JsonResponse({
                "success": False,
                "error": "YouTube URL Required"
            }, status=400)
        video_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'tags': data.get('tags'),
            'categoryId': data.get('categoryId')
        }
        video_data = {k: v for k, v in video_data.items() if v if not None} #AI to solve issue
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return JsonResponse({
                "success": False,
                "error": "Invalid YouTube URL"
            }, status=400)
        log(f"Update_Found_ID : {video_id}")
    
        url = "https://www.googleapis.com/youtube/v3/videos"
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        get_response = requests.get(
            f"{url}?id={video_id}&part=snippet,status",
            headers=headers
        )

        log(f"Update_Get_Info : {get_response}")

        response_data = get_response.json()
        video_resource = response_data.get("items", [])[0] if response_data.get("items") else None
        if not video_resource:
            return JsonResponse({
                "success": False,
                "error": "Video not Found"
            }, status=404)
    
        snippet = video_resource.get("snippet", {})
        for key, value in video_data.items():
            if key in snippet:
                snippet[key] = value

        update_data = {
            "id": video_id,
            "snippet": snippet,
            "status": video_resource.get("status", {})
        }

        update_response = requests.put(
            f"{url}?part=snippet,status",
            headers=headers,
            json=update_data
        )

        log(f"Updated : {update_response}")

        if update_response.status_code == 200:
            return JsonResponse({"success":True, "message":"Video Update Success"}, status=200)
        else:
            try:
                error_data = update_response.json()
                return JsonResponse({"success":False, "error": error_data.get("error", {}).get("message", "Unknown Error")}, status=update_response.status_code)
            except ValueError:
                return JsonResponse({"success":False, "error": f"Status Code: {update_response.status_code}"}, status=update_response.status_code)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in Request Body"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_POST
def delete_youtube_video(request):
    log(f"Called_Delete_Youtube_Video")
    try:
        access_token = extract_token_from_header(request)
        if not access_token:
            return JsonResponse({
                "success": False,
                "error": "No Auth Token Provided"
            }, status=401)
        
        data = json.loads(request.body)
        youtube_url = data.get("youtube_url")
        if not youtube_url:
            return JsonResponse({
                "success": False,
                "error": "YouTube URL Required"
            }, status=400)
        
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return JsonResponse({
                "success": False,
                "error": "Invalid YouTube URL"
            }, status=400)
        
        log(f"Deleting_ID : {video_id}")
    
        #url = f"https://www.googleapis.com/youtube/v3/video?id={video_id}"
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        log(f"Delete_Response : {response}")

        if response.status_code == 204:
            return JsonResponse({
                "success": True,
                "message": f"Video {video_id} Deletion Success"
            })
        else:
            try:
                error_data = response.json()
                return JsonResponse({
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Unknown Error")
                }, status=response.status_code)
            except ValueError:
                return JsonResponse({
                    "success": False,
                    "error": f"Status Code: {response.status_code}"
                }, status=response.status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in Request Body"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def check_task_status(request, task_id):
    log(f"Called_Check_Task_Status")
    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse({"status": "completed", "result": result.result})
    return JsonResponse({"status": "pending"})

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def ensure_playlist(request):
    log("Attempting playlist ensure")

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
            log(f"PLAYLIST TASK ID: {task_result.id}")

            return JsonResponse({f"task_id":task_result.id}, status=202)
    except Exception as e:
        logger.error(f"Playlist Ensure attempted but failed: {e}")
        return JsonResponse({"error": "Internal Server Error in Playlist Ensure"}, status=500)

@csrf_exempt #Disable CSRF, need Proper Authentication CHANGE
def store_link(request):
    log("Attempting video link")

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
            log(f"LINKED : {video_url}")
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
    log("Attempting video upload")

    #Ensure POST is used to give data to backend
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
       # Ensure it's a file upload request that can hold a file as JSON will not
        if request.content_type.startswith("multipart/form-data"):
            log("Processing multipart/form-data request")

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
            log(f"Received title: {title}, description: {description}")
            log(f"Access Token: {access_token}")
            log(f"Received file: {file.name} (Size: {file.size} bytes)")

            #Read file and encode to base64 for transfer
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode()

            log("Attempting YT Video Enqueue")
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
            log("YouTube video queued")

            if(upload_res == 0):
                return JsonResponse({"message": "File uploaded successfully", "filename": file.name}, status=200,)
            else:
                return JsonResponse({"message": "File upload failure"}, status=500)
        else:
            return JsonResponse({"error": "Invalid Content-Type"}, status=400)
    except Exception as e:
        logger.error(f"Upload attempted but failed using Redis/Celery: {e}")
        log(f"Upload_Retry_Without_CeleRedis")

        try:
            #ReBuild information from above, but instead of task do here
            file = request.FILES.get("file")
            title = request.POST.get("title")
            description = request.POST.get("description")
            lesson_id = request.POST.get("lesson_id")
            playlist = request.POST.get("playlist")
            access_token = request.POST.get("accessToken")
            if not file:
                return JsonResponse({"error": "File is required"}, status=400)
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode()
            #file_base64, file.size, title, description, access_token, lesson_id, playlist

            #COPIED CODE FROM tasks.py upload_to_youtube task
            if(lesson_id is None):
                return JsonResponse({"error": "Lesson ID None"}, status=400)
            try:
                # https://developers.google.com/youtube/v3/docs/videos/insert#.net
                # Documentations on insert/upload YT functionality
                metadata = {
                    "snippet":{
                        "title":title,
                        "description":description,
                        "tags":["Test"], #Will need to swap out for user provided course tags CHANGE
                        "categoryId": "27", #educational lock
                    },
                    "status":{
                        "madeForKids":False, #Might not function as intended anymore CHANGE
                        "privacyStatus": "public",
                    }
                }
                headers = {
                    "Authorization":f"Bearer {access_token}" #Use our ClientID with UserAuth
                }

                #Post request to youtube to get resumable URL
                init_response = requests.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos",
                    params={
                        "part":"snippet, status", 
                        "uploadType":"resumable"
                    },
                    headers=headers,
                    json=metadata
                )

                if init_response.status_code != 200:
                    raise Exception(f"Error intiating upload: {init_response.text}")
                resumable_url = init_response.headers['Location']

                #decode b64 to binary
                file_data = base64.b64decode(file_base64)
                #Use resumable URL to upload video binary data
                upload_response = requests.put(
                    resumable_url,
                    headers={
                        "Content-Type": "video/mp4",
                        "Content-Length": str(file.size)
                    },
                    data=file_data
                )
                
                if upload_response.status_code != 200:
                    raise Exception(f"Error uploading video: {upload_response.text}")

                response_dict = upload_response.json()
                video_id = response_dict.get("id")
                logger.debug(f'Youtube_Link https://www.youtube.com/watch?v={video_id}')

                lesson_id = int(lesson_id)
                lesson = Lessons.objects.get(lessonID=lesson_id)
                upload = Uploaded.objects.create(lessonID=lesson, videoURL="https://www.youtube.com/watch?v="+video_id)
                logger.debug(f"Upload_Status {upload}")

                #If a playlist is given
                #CHANGE if fixing playlist feature
                    
                return JsonResponse({"message": "File uploaded successfully", "filename": file.name}, status=200,)
            
            except Exception as e:
                logger.debug(f"Upload Error {str(e)}")
                return JsonResponse({"error": "Internal Server Error in Upload"}, status=500)
        except Exception as e:
            logger.debug(f"Upload Error {str(e)}")
            return JsonResponse({"error": "Internal Server Error in Upload Outer?"}, status=500)

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

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = Lessons.objects.filter(courseID=course).prefetch_related('uploaded_set')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonViewAll(viewsets.ModelViewSet):
    queryset = Lessons.objects.all().prefetch_related('uploaded_set')
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
