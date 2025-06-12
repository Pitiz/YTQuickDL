from flask import Flask, request, jsonify, render_template
from logic import load_playlist
from logic import download_url_list


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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

    download_url_list(urls, format, dest_folder)

    return {'status': 'success', 'message': f'Downloaded {len(urls)} files in {format} format.'}

if __name__ == '__main__':
    app.run(debug=True)