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
    
    # Ye line YouTube ke bot check ko bypass karti hai (Android client use karke)
    common_opts = {
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')
    }
    
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
