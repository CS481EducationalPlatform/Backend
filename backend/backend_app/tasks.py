import base64
import logging
from .models import Uploaded, Lessons
from celery import shared_task
import requests
from dotenv import load_dotenv
from django.conf import settings

logger = logging.getLogger("django")
load_dotenv()

@shared_task
def link_uploaded(lesson_id, video_url):
    if "https://www.youtube.com/watch?v=" not in video_url and "https://youtu.be/" not in video_url:
        logger.debug("Improperly formatted youtube link")
        return 13 # Data Invalid

    lesson = Lessons.objects.get(lessonID=lesson_id)
    upload = Uploaded.objects.create(lessonID=lesson, videoURL=video_url)
    logger.debug(f"Upload_Status {upload}")
    return 0 #good

@shared_task
def ensure_playlist_exists(playlist_name, access_token):
    #Create a header for auth and type for multi-use
    url="https://youtube.googleapis.com/youtube/v3/playlists"
    headers={
        "Authorization":f"Bearer {access_token}", #Use our ClientID with UserAuth
        "Accept": "application/json"
    }
    params={
        "part": "snippet",
        "maxResults": 50,
        "mine": "true"
    }
    #api_key=settings.YOUTUBE_API_KEY

    #Make a get request to get playlists by account
    '''
    playlist_response = requests.get(
        "https://www.googleapis.com/youtube/v3/playlists",
        params={
            "part": "snippet",
            "mine": True,
            "maxResults": 50
        },
        headers=headers
    )
    '''
    '''
    playlist_response = requests.get(
        f"https://youtube.googleapis.com/youtube/v3/playlists?part=snippet&maxResults=50&mine=true&key={api_key}",
        headers=headers
    )
    '''

    playlist_response = requests.get(
        url,
        headers=headers,
        params=params
    )

    logger.debug(f"Playlist_Code : {playlist_response.status_code}")

    #Create id object for tracking id
    playlist_id = None

    #Ensure code is good response
    if 200 == 200:
        # Pull list of playlists from response (response has items which is array)
        playlists = playlist_response.json().get("items", [])
        logger.debug("Playlist_Out")
        logger.debug(playlists)
        #Parse list for desired name and get id if exists
        for playlist in playlists:
            logger.debug(f"Playlist_# : {playlist}")
            # earlier call requested snippet information which includes title
            if playlist["snippet"]["title"] == playlist_name:
                logger.debug("Playlist_Found")
                playlist_id = playlist["id"]
        
        #If playlist not found -> create
        if playlist_id is None:
            logger.debug("Playlist_Create")
            #Create snippet/status pair to create playlist with post
            data = {
                "snippet": {
                    "title": playlist_name,
                    "description": f"Playlist created with name {playlist_name} via BabushkaLessons"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }

            #create playlist with post
            playlist_create_response = requests.post(
                "https://www.googleapis.com/youtube/v3/playlists",
                params={
                    "part":"snippet, status"
                },
                headers=headers,
                json=data
            )

            if playlist_create_response.status_code == 200:
                playlist_id = playlist_create_response.json()["id"]

    # return None | id
    logger.debug(f"Playlist_ID : {playlist_id}")
    return playlist_id

@shared_task
def upload_to_youtube(file_base64, file_size, title, description, access_token, lesson_id, playlist):
    if(lesson_id is None):
        return "Error lesson id none"
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
                "Content-Length": str(file_size)
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
        playlist = None
        if playlist is not None and playlist != "":
            #Get id of playlist to add to
            playlist_id = ensure_playlist_exists(playlist_name=playlist, access_token=access_token)
            #add uploaded video to playlist via both IDs
            
            if playlist_id is not None:
                #setup data
                playlist_data = {
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }

                #Post video into playlist
                playlist_response = requests.post(
                    "https://www.googleapis.com/youtube/v3/playlistItems",
                    params={
                        "part": "snippet"
                    },
                    headers=headers,
                    json=playlist_data
                )

                logger.debug("Playlist_Response")
                logger.debug(playlist_response)

                #Make sure work or return unique code (2)
                if playlist_response.status_code != 200:
                    return 2
            else:
                return 3
            
        return 0
    
    except Exception as e:
        logger.debug(f"Upload Error {str(e)}")
        return 1
