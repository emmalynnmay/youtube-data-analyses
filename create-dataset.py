from googleapiclient.discovery import build
from dotenv import dotenv_values
import pandas as pd

config = dotenv_values('.env')

VIDEO_IDS = ['ZEV7ksLS5dk', 'ZbKd9AuncNI', 'jfWa-GD0szU']
OUTPUT_NAME = 'output.csv'

def authenticate():
    if config['YOUTUBE_API_KEY'] == '':
        raise Exception('You must add a YouTube API key to the .env file to run this script!')
    return build('youtube', 'v3', developerKey=config['YOUTUBE_API_KEY'])

def get_video_data(youtube, vid_id):
    request = youtube.videos().list(
        part='snippet',
        id=vid_id
    )
    response = request.execute()
    return response['items'][0]

def clean_string_for_csv(string):
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace(',', '\\,')
    return string

def pull_data_for_list(youtube, list, object_type):
    data = []
    for item in list:
        if object_type == 'video':
            result = get_video_data(youtube, item)
            to_add = {'id': item}
            result['snippet']['description'] = clean_string_for_csv(result['snippet']['description'])
            del result['snippet']['thumbnails']
            del result['snippet']['localized'] #TODO: do we want to add this back?
            to_add = {**to_add, **(result['snippet'])}
            data.append(to_add)

    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    youtube = authenticate()
    videos = pull_data_for_list(youtube, VIDEO_IDS, 'video')
    videos.to_csv(OUTPUT_NAME, index=False)
