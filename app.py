from flask import Flask, request, send_from_directory, jsonify
import os
import yt_dlp as youtube_dl

app = Flask(__name__)

progress_data = {
    'total_videos': 0,
    'videos_downloaded': 0
}

def download_video(video_url, download_path, progress_callback=None):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_callback] if progress_callback else [],
        'nocheckcertificate': True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False
    return True

def progress_hook(d):
    if d['status'] == 'downloading':
        percentage = d['_percent_str'].strip()
        print(f"Downloading: {percentage}")
    elif d['status'] == 'finished':
        progress_data['videos_downloaded'] += 1
        print(f"Downloaded: {d['filename']}")

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    global progress_data
    download_path = request.json.get('download_path')
    video_url = request.json.get('video_url')

    if not download_path or not video_url:
        return jsonify({"status": "error", "message": "Missing download path or video URL"}), 400

    progress_data = {
        'total_videos': 1,
        'videos_downloaded': 0
    }

    success = download_video(video_url, download_path, progress_callback=progress_hook)
    if success:
        return jsonify({"status": "Download Complete", "remaining": progress_data['total_videos'] - progress_data['videos_downloaded']})
    else:
        return jsonify({"status": "error", "message": "Failed to download video"}), 500

if __name__ == '__main__':
    app.run(debug=True)
