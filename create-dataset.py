from googleapiclient.discovery import build
from dotenv import dotenv_values

config = dotenv_values(".env")

def pull_data():

    print(config)

    youtube = build('youtube', 'v3', developerKey=config['YOUTUBE_API_KEY'])

    request = youtube.videos().list(
        part="snippet,contentDetails",
        id="ZEV7ksLS5dk"
    )
    response = request.execute()

    title = response['items'][0]['snippet']['title']
    duration = response['items'][0]['contentDetails']['duration']
    thumbnail_url = response['items'][0]['snippet']['thumbnails']['default']['url']

    print("Title: ", title)
    print("Duration: ", duration)
    print("Thumbnail URL: ", thumbnail_url)

if __name__ == "__main__":
    pull_data()
