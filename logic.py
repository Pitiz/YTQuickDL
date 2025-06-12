import yt_dlp
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
    

# dest_folder = input("Name the folder where the files will be saved:")

# valid_formats = ["flac", "mp3", "wav"]
# selected_format = ""

# while True:
#     user_input = input("Please enter a format (flac, mp3, wav): ").lower()
#     if user_input in valid_formats:
#         selected_format = user_input
#         break
#     else:
#         print("Invalid input. Please try again.")


def download_url_list(urls, format, dest_folder):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet' : True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '0',
        }],
        'outtmpl': dest_folder+'/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            print(url)
            try:
                print(f"Downloading: {url['title']}")
                ydl.download(url['url'])
            except Exception as e:
                print(f"Failed to download: {e}")
