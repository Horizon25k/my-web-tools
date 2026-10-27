from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import os
import tempfile
import yt_dlp
import urllib.request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # อนุญาตให้หน้าเว็บ HTML เรียกใช้ API ได้

# ==========================================
# 1. Page Routes (หน้าเว็บหลักและเครื่องมือต่างๆ)
# ==========================================

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/x-downloader.html', methods=['GET'])
def x_downloader_page():
    return render_template('x-downloader.html')

@app.route('/webp_pdf.html', methods=['GET'])
def webp_pdf_page():
    return render_template('webp_pdf.html')

@app.route('/tiktok-downloader.html', methods=['GET'])
def tiktok_downloader_page():
    return render_template('tiktok-downloader.html')

@app.route('/pdf_merge.html', methods=['GET'])
def pdf_merge_page():
    return render_template('pdf_merge.html')

@app.route('/youtube-downloader.html', methods=['GET'])
def youtube_downloader_page():
    return render_template('youtube-downloader.html')

@app.route('/public/<path:filename>', methods=['GET'])
def serve_public_files(filename):
    return send_from_directory('public', filename)

# ==========================================
# 2. API Endpoints (ระบบเบื้องหลัง)
# ==========================================

# API สำหรับ X (Twitter) Downloader
@app.route('/api/get_x_video', methods=['POST'])
def get_x_video():
    data = request.json or {}
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'กรุณาส่งลิงก์มาด้วย'}), 400

    cookie_content = os.environ.get('COOKIE_CONTENT', '')
    cookie_file_path = ''

    if cookie_content:
        tf = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8')
        tf.write(cookie_content)
        tf.close()
        cookie_file_path = tf.name

    ydl_opts = {
        'cookiefile': cookie_file_path if cookie_file_path else None, 
        'quiet': True,
        'skip_download': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
            
            if cookie_file_path and os.path.exists(cookie_file_path):
                os.unlink(cookie_file_path)

            if not mp4_formats:
                return jsonify({'error': 'ไม่พบไฟล์วิดีโอ'}), 404
                
            best_video = sorted(mp4_formats, key=lambda x: x.get('height', 0), reverse=True)[0]
            
            filesize = best_video.get('filesize') or best_video.get('filesize_approx') or 0
            
            return jsonify({
                'author': info.get('uploader', 'Unknown'),
                'author_id': info.get('uploader_id', ''),
                'text': info.get('title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': best_video.get('url'),
                'filesize': filesize
            })
            
    except Exception as e:
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.unlink(cookie_file_path)
        return jsonify({'error': str(e)}), 500

# API สำหรับ YouTube Downloader
@app.route('/api/get_youtube_video', methods=['POST'])
def get_youtube_video():
    data = request.json or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'กรุณาระบุ URL วิดีโอ YouTube'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_url = info.get('url')
            thumbnail = info.get('thumbnail')
            title = info.get('title', 'YouTube Video')
            author = info.get('uploader') or info.get('channel', 'YouTube Creator')
            duration = info.get('duration', 0)
            filesize = info.get('filesize') or info.get('filesize_approx', 0)

            return jsonify({
                'title': title,
                'author': author,
                'thumbnail': thumbnail,
                'duration': duration,
                'filesize': filesize,
                'video_url': video_url,
                'audio_url': video_url
            })

    except Exception as e:
        return jsonify({'error': f'ไม่สามารถดึงข้อมูลได้: {str(e)}'}), 500

# ระบบบังคับดาวน์โหลดไฟล์ (Proxy Download Stream)
@app.route('/api/force_download', methods=['GET'])
def force_download():
    video_url = request.args.get('url')
    if not video_url:
        return "ไม่มี URL", 400
        
    def generate():
        req = urllib.request.Request(video_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                yield chunk

    return Response(
        generate(),
        mimetype='video/mp4',
        headers={'Content-Disposition': 'attachment; filename="downloaded-video.mp4"'}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"เปิดเซิร์ฟเวอร์แล้ว กำลังรันอยู่ที่พอร์ต {port}")
    app.run(host='0.0.0.0', port=port)