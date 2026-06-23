import os
import tempfile
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']
    
    temp_dir = tempfile.mkdtemp()
    
    # Render Environment se cookies ko read karna
    cookies_str = os.environ.get('YOUTUBE_COOKIES')
    cookie_file_path = None
    
    if cookies_str:
        # Cookies ko ek temporary file mein save karna
        cookie_file_path = os.path.join(temp_dir, 'cookies.txt')
        with open(cookie_file_path, 'w') as f:
            f.write(cookies_str)

    common_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')
    }
    
    # Agar cookies mil gayi toh unhe use karna
    if cookie_file_path:
        common_opts['cookiefile'] = cookie_file_path

    # Web client use karna cookies ke saath
    common_opts['extractor_args'] = {'youtube': {'player_client': ['web']}}

    if format_type == 'audio':
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            **common_opts,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)} <br><br><a href='/'>Wapas jayein</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
