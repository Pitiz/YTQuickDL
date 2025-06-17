from flask import Flask, request, Response, jsonify, render_template, session
import webbrowser
from flask import send_from_directory
import os
import yt_dlp
import threading
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',mimetype='image/vnd.microsoft.icon')
    
@app.route('/load', methods=['POST'])
def load_data():
    data = request.json
    url = data.get('url')
    result = load_playlist(url)
    return jsonify(result)

def handle_download(item, format, dest_folder):
    print("Started download for " + str(item['id']))
    progress_data[item['id']] = '0.0%'
    download_url(item, format, dest_folder)

@app.route('/download', methods=['POST'])
def download_urls():
    threads = []
    data = request.json
    urls = data.get('urls')
    format = data.get('format')

    dest_folder = data.get('dest_folder')

    if not dest_folder:
        dest_folder = "Downloads"
        
    if not urls or not format:
        return {'status': 'error', 'message': 'Missing URLs or format.'}, 400

    for item in urls:
        t = threading.Thread(target=handle_download, args=(item, format, dest_folder))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        
    return {'status': 'success', 'message': 'Download completed.'}, 200

@app.route('/progress/<id>', methods=['GET'])
def progress_stream(id):
    if progress_data is None or not progress_data:
        return Response("No data", 401)
    
    if id not in progress_data:
        return Response("Not found", 404)
    
    percentage = str(progress_data[id])
    return percentage, 200

def open_browser():
      webbrowser.open_new("http://127.0.0.1:5000")
      
def load_playlist(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(playlist_url, download=False)

    urls = list()

    for video in playlist_dict['entries']:
        urls.append({
            'url' : video['url'],
            'title' : video['title']
        })

    # print(f"Number of videos loaded from playlist: {len(urls)}")
    return urls
    
progress_data = {}
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            progress_data[item['id']] = '0.0%'
            dl_result = ydl.download(item['url'])
        
            if(dl_result == 0):
                progress_data[item['id']] = '100.0%'
            else:
                progress_data[item['id']] = 'FAILED'
                
        except Exception as e:
            print(f"Failed to download: {e}")
            pass

if __name__ == "__main__":
    app.secret_key = os.urandom(16)
    app.run(debug=True)