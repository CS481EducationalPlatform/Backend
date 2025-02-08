import base64
import logging
from celery import shared_task
import requests
from dotenv import load_dotenv

logger = logging.getLogger("django")
load_dotenv()

@shared_task
def upload_to_youtube(file_base64, file_name, file_size, title, description, user_id, course_id, page_id, access_token):
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

        logger.debug(f'REQ_OUT {upload_response}')

        return "Upload completed successfully!"
    except Exception as e:
        logger.debug("Upload Error")
        return f"Error during upload: {str(e)}"
