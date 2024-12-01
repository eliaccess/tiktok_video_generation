import json
import requests

curl_request_login = """
curl --location --request POST 'https://open.tiktokapis.com/v2/oauth/token/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Cache-Control: no-cache' \
--data-urlencode 'client_key=CLIENT_KEY' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'code=CODE' \
--data-urlencode 'grant_type=authorization_code' \
--data-urlencode 'redirect_uri=REDIRECT_URI'
"""

CLIENT_KEY = "sbawj8h978uut4r23w"
CLIENT_PASSWORD = "vkQ0AdoEgqe1CvkWwz61pA0005ZNoHny"

def request_login():
    url = 'https://open.tiktokapis.com/v2/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_PASSWORD,
        "grant_type": "authorization_code",
        "code": "CODE"
    }
    # Run the curl command and return the output
    return requests.post(url, headers=headers, data=data)

# request an access token
login_response = request_login()
print(login_response.json())

curl_request_upload = """
curl --location 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/' \
--header 'Authorization: Bearer act.example12345Example12345Example' \
--header 'Content-Type: application/json' \
--data '{
    "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": exampleVideoSize,
        "chunk_size" : exampleVideoSize,
        "total_chunk_count": 1
    }
}'
"""

