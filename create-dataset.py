from googleapiclient.discovery import build
from dotenv import dotenv_values
import pandas as pd

config = dotenv_values('.env')

VIDEO_IDS = ['ZEV7ksLS5dk', 'ZbKd9AuncNI', 'jfWa-GD0szU']
PLAYLIST_ID = 'PLCow7UQsPflmxuJnkVv1oEkanC3-ZDvmG'
OUTPUT_NAME = 'new-youtube-data.csv'

def authenticate():
    if config['YOUTUBE_API_KEY'] == '':
        raise Exception('You must add a YouTube API key to the .env file to run this script!')
    return build('youtube', 'v3', developerKey=config['YOUTUBE_API_KEY'])

def clean_string_for_csv(string):
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace(',', '\\,')
    return string

def clean_video_data(vid_data):

    vid_data['snippet']['description'] = clean_string_for_csv(vid_data['snippet']['description'])
    del vid_data['snippet']['thumbnails']
    del vid_data['snippet']['localized'] 
    del vid_data['snippet']['channelId'] 
    del vid_data['snippet']['liveBroadcastContent'] 

    del vid_data['contentDetails']['dimension']
    del vid_data['contentDetails']['contentRating']
    del vid_data['contentDetails']['projection']

    return vid_data

def get_video_data(youtube, vid_id):
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics,paidProductPlacementDetails,topicDetails',
        id=vid_id
    )
    response = request.execute()
    return clean_video_data(response['items'][0])

def pull_data_for_list(youtube, list, object_type, genre):
    data = []
    for item in list:
        if object_type == 'video':
            result = get_video_data(youtube, item)
            to_add = {'id': item, 'genre': genre}
            to_add = {**to_add, **(result['snippet'])}
            to_add = {**to_add, **(result['contentDetails'])}
            to_add = {**to_add, **(result['statistics'])}
            to_add = {**to_add, **(result['paidProductPlacementDetails'])}
            to_add = {**to_add, **(result['topicDetails'])}
            data.append(to_add)

    df = pd.DataFrame(data)
    return df

def get_ids_in_playlist(youtube, playlist_id):
    to_return = []

    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id
    )
    response = request.execute()
    
    for vid in response['items']:
        to_return.append(vid['contentDetails']['videoId'])

    return to_return

if __name__ == '__main__':
    youtube = authenticate()
    ids_in_playlist = get_ids_in_playlist(youtube, PLAYLIST_ID)
    videos = pull_data_for_list(youtube, ids_in_playlist, 'video', 'USU')
    videos.to_csv(OUTPUT_NAME, index=False)
