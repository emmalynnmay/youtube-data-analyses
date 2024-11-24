from googleapiclient.discovery import build
from dotenv import dotenv_values
import pandas as pd

config = dotenv_values('.env')

TEST_VIDEO_IDS = ['ZEV7ksLS5dk', 'ZbKd9AuncNI', 'jfWa-GD0szU']
TEST_PLAYLIST_ID = 'PLCow7UQsPflmxuJnkVv1oEkanC3-ZDvmG'
PLAYLISTS = {
    'Slam Poetry': 'PL9rT6KUep7uqN8Xioo3R32cUyogH5wVMk',
    'Minecraft': 'PLKiPmtkaxvOYFJzP847fBEfpr4FZD3tpg',
    'Movie Scenes': 'PLYhREcq3PbZ8duNVstBQ_0jnHC1ffxJfu',
    'Woodworking': 'PLr6O8F0Sz5TrKaAzGdhmmkIoxE-vdRYDE',
    'Space Songs': 'PLG04vLHTI500i3IcAK5Xsgn9F2q66ZOgr',
    'Ancient Memes': 'PLHEBsC_NxJ_R3KnXJa4BfF7NEbnNvW_jg'
    }
OUTPUT_NAME = 'new-youtube-data.csv'
PAGE_COUNT_LIMIT = 50

def authenticate():
    if config['YOUTUBE_API_KEY'] == '':
        raise Exception('You must add a YouTube API key to the .env file to run this script!')
    return build('youtube', 'v3', developerKey=config['YOUTUBE_API_KEY'])

def clean_string_for_csv(string):
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace(',', '\\,')
    return string

def clean_video_data(vid_data, item, genre):

    vid_data['snippet']['description'] = clean_string_for_csv(vid_data['snippet']['description'])
    del vid_data['snippet']['thumbnails']
    del vid_data['snippet']['localized'] 
    del vid_data['snippet']['channelId'] 
    del vid_data['snippet']['liveBroadcastContent'] 

    del vid_data['contentDetails']['dimension']
    del vid_data['contentDetails']['contentRating']
    del vid_data['contentDetails']['projection']

    to_add = {'id': item, 'genre': genre}
    to_add = {**to_add, **(vid_data['snippet'])}
    to_add = {**to_add, **(vid_data['contentDetails'])}
    to_add = {**to_add, **(vid_data['statistics'])}
    to_add = {**to_add, **(vid_data['paidProductPlacementDetails'])}
    to_add = {**to_add, **(vid_data['topicDetails'])}

    return to_add

def get_video_data(youtube, vid_id, genre):
    print(f"   Pulling data for {vid_id}")

    request = youtube.videos().list(
        part='snippet,contentDetails,statistics,paidProductPlacementDetails,topicDetails',
        id=vid_id
    )
    
    response = request.execute()
    if len(response['items']) == 0:
        print("      Video not available :(")
        return None

    return clean_video_data(response['items'][0], vid_id, genre)

def pull_data_for_list(youtube, list, object_type, genre):
    data = []
    for item in list:
        if object_type == 'video':
            try:
                result = get_video_data(youtube, item, genre)
                if result != None:
                    data.append(result)
            except:
                continue

    df = pd.DataFrame(data)
    return df

def check_if_exists(response, key):
    try:
        result = response[key]
        return True
    except:
        return False

def get_ids_in_playlist(youtube, playlist_id):
    to_return = []

    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=PAGE_COUNT_LIMIT,
    )
    response = request.execute()
    
    for vid in response['items']:
        to_return.append(vid['contentDetails']['videoId'])

    if check_if_exists(response, 'nextPageToken'):
        next_page_token = response['nextPageToken']

        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=PAGE_COUNT_LIMIT,
                pageToken=next_page_token
            )
            response = request.execute()
            for vid in response['items']:
                to_return.append(vid['contentDetails']['videoId'])

            if check_if_exists(response, 'nextPageToken'):
                next_page_token = response['nextPageToken']
            else:
                break

    return to_return

def create_dataset(youtube):
    video_collections = []

    for playlist_name, playlist_id in PLAYLISTS.items():
        print(f"Pulling video data for playlist {playlist_name}...")
        ids_in_playlist = get_ids_in_playlist(youtube, playlist_id)
        print(f"   Found {len(ids_in_playlist)} video ids...")
        videos = pull_data_for_list(youtube, ids_in_playlist, 'video', playlist_name)
        video_collections.append(videos)

    full_list = pd.concat(video_collections)
    full_list.to_csv(OUTPUT_NAME, index=False)

if __name__ == '__main__':
    youtube = authenticate()
    create_dataset(youtube)
