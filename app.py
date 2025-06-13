from flask import Flask, request, jsonify, render_template
from logic import load_playlist
from logic import download_url_list
import webbrowser
from flask import send_from_directory
import os
from threading import Timer

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


@app.route('/download', methods=['POST'])
def download_urls():
    data = request.json
    urls = data.get('urls')
    
    format = data.get('format')

    if not urls or not format:
        return {'status': 'error', 'message': 'Missing URLs or format.'}, 400

    dest_folder = './downloads'

    return download_url_list(urls, format, dest_folder), 200


def open_browser():
      webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)