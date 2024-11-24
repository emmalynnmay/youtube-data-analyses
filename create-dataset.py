from googleapiclient.discovery import build
from dotenv import dotenv_values
import pandas as pd

config = dotenv_values('.env')

TEST_VIDEO_IDS = ['ZEV7ksLS5dk', 'ZbKd9AuncNI', 'jfWa-GD0szU']
TEST_PLAYLIST_ID = 'PLCow7UQsPflmxuJnkVv1oEkanC3-ZDvmG'
PLAYLISTS = {
    #'USU': TEST_PLAYLIST_ID}
    'Slam Poetry': 'PL9rT6KUep7uqN8Xioo3R32cUyogH5wVMk'}
    # 'Minecraft': 'PLKiPmtkaxvOYFJzP847fBEfpr4FZD3tpg',
    # 'Movie Scenes': 'PLYhREcq3PbZ8duNVstBQ_0jnHC1ffxJfu',
    # 'Woodworking': 'PLr6O8F0Sz5TrKaAzGdhmmkIoxE-vdRYDE',
    # 'Space Songs': 'PLG04vLHTI500i3IcAK5Xsgn9F2q66ZOgr',
    # 'Ancient Memes': 'PLHEBsC_NxJ_R3KnXJa4BfF7NEbnNvW_jg'
    # }
OUTPUT_NAME = 'new-youtube-data.csv'
PAGE_COUNT_LIMIT = 4#49

def authenticate():
    if config['YOUTUBE_API_KEY'] == '':
        raise Exception('You must add a YouTube API key to the .env file to run this script!')
    return build('youtube', 'v3', developerKey=config['YOUTUBE_API_KEY'])

def clean_string_for_csv(string):
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace(',', '\\,')
    return string

def format_ids(id_list):
    ids = ''
    for the_id in id_list:
        ids += (the_id + ',')
    return ids + "hey"
    return ids[:-1]

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

def get_video_data(youtube, vid_ids, vid_ids_formatted, genre):
    print(vid_ids)
    print(vid_ids_formatted)

    request = youtube.videos().list(
        part='snippet,contentDetails,statistics,paidProductPlacementDetails,topicDetails',
        id=vid_ids_formatted
    )
    response = request.execute()

    to_return = []
    print(f"Length: {len(vid_ids)}")
    for vid_index in range(len(vid_ids)):

        if vid_index >= len(vid_ids):
            print("Huh that's weird")
            continue

        print(vid_index)
        to_return.append(clean_video_data(response['items'][vid_index], vid_ids[vid_index], genre))
    
    return to_return

def pull_data_for_list(youtube, list, object_type, genre):
    data = []
    index = 0
    while True:
        print(f"   Getting videos {index} to {index + PAGE_COUNT_LIMIT - 1}")
        this_batch_of_ids = format_ids(list[index:index + PAGE_COUNT_LIMIT])
        if object_type == 'video':
            result = get_video_data(youtube, list[index:index + PAGE_COUNT_LIMIT], this_batch_of_ids, genre)
            data += result
        else:
            raise Exception(f"Object type {object_type} not recognized.")
        
        if index + PAGE_COUNT_LIMIT <= len(list) - 1:
            index += (PAGE_COUNT_LIMIT - 1)
        else:
            break

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

def create_dataset(youtube):
    video_collections = []

    for playlist_name, playlist_id in PLAYLISTS.items():
        print(f"Pulling video data for playlist {playlist_name}...")
        ids_in_playlist = get_ids_in_playlist(youtube, playlist_id)
        print(f"All the ids: {ids_in_playlist}")
        videos = pull_data_for_list(youtube, ids_in_playlist, 'video', playlist_name)
        video_collections.append(videos)

    full_list = pd.concat(video_collections)
    full_list.to_csv(OUTPUT_NAME, index=False)

if __name__ == '__main__':
    youtube = authenticate()
    create_dataset(youtube)
