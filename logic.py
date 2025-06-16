import yt_dlp
import threading
import re
#Install yt_dlp using:      pip.exe install git+https://github.com/nficano/pytube

# playlist_url = "https://www.youtube.com/playlist?list=PLSNrCkxRaAmqvzm3TnSEQx-eJdLSjwnIS" #groove
# playlist_url = "https://www.youtube.com/playlist?list=PLWcttt0SQjI_i-Hgib9xytPKPscMPFSlL" #tech house


def load_playlist(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    print("Loading... This might take some time depending on the size of the playlist.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(playlist_url, download=False)

    urls = list()

    for video in playlist_dict['entries']:
        urls.append({
            'url' : video['url'],
            'title' : video['title']
        })

    print(f"Number of videos loaded from playlist: {len(urls)}")
    
    return urls
    
progress_data = {}
counter_lock = threading.Lock()
def create_hook(item):  
    def progress_hook(d):
        if d['status'] == 'downloading':
            percentage = d.get('_percent_str', '0.0%')
            ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
            clean_text = ansi_escape.sub('', percentage)
            
            progress_data[item['id']] = clean_text
    return progress_hook

def download_url(item, format, dest_folder):
    # item:
    #     id
    #     url
    #     title
    hook = create_hook(item)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet' : True,
        'progress_hooks': [hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '0',
        }],
        'outtmpl': dest_folder+'/%(title)s.%(ext)s',
    }
    
    success_counter = 0
    fail_counter = 0

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            with counter_lock:
                progress_data[item['id']] = 'Starting...'
                dl_result = ydl.download(item['url'])
            
                if(dl_result == 0):
                    success_counter+=1
                    progress_data[item['id']] = '100.0%'
                else:
                    fail_counter+=1
                    progress_data[item['id']] = 'FAILED'
                
        except Exception as e:
            with counter_lock:
                fail_counter+=1
            print(f"Failed to download: {e}")
            pass           

# def download_url_list(urls, format, dest_folder):
#     def progress_hook(d):
#         if d['status'] == 'downloading':
#             percentage = d.get('_percent_str', '0.0%')
#             progress_data[int(urls['id'])] = percentage
#             print("Updated data")

#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'quiet' : True,
#         'progress_hooks': [progress_hook],
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': format,
#             'preferredquality': '0',
#         }],
#         'outtmpl': dest_folder+'/%(title)s.%(ext)s',
#     }
    
#     success_counter = 0
#     fail_counter = 0

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         for url in urls:
#             try:
#                 progress_data[int(urls['id'])] = 'STARTING...'
#                 print(f"Downloading: {url['title']}")
#                 dl_result = ydl.download(url['url'])
                
#                 if(dl_result == 0):
#                     success_counter+=1
#                 else:
#                     progress_data[int(urls['id'])] = 'FAILED'
#                     fail_counter+=1
                    
#             except Exception as e:
#                 fail_counter+=1
#                 print(f"Failed to download: {e}")
#                 pass
            
#             progress_data[int(urls['id'])] = '100.0%'
        
#         return "Download finished. "+ str(success_counter)+ " downloaded. "+ str(fail_counter) + " failed."