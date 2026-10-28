from flask import Flask, request, jsonify, render_template, send_from_directory, Response, send_file
import os
import tempfile
import yt_dlp
import urllib.request
from dotenv import load_dotenv
load_dotenv()
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

# ==========================================
# API 1: ดึงข้อมูลและรายการความละเอียดทั้งหมดพร้อมขนาดไฟล์
# ==========================================
@app.route('/api/get_youtube_video', methods=['POST'])
def get_youtube_video():
    data = request.json or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'กรุณาระบุ URL'}), 400
    
    if '?si=' in url: url = url.split('?si=')[0]
    if '&si=' in url: url = url.split('&si=')[0]

    cookie_content = os.environ.get('YOUTUBE_COOKIE_CONTENT', '')
    if not cookie_content or len(cookie_content.strip()) <= 20:
        return jsonify({'error': 'กรุณาตั้งค่า YOUTUBE_COOKIE_CONTENT ในไฟล์ .env'}), 400

    cookie_file = ''
    try:
        tf = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8')
        tf.write(cookie_content)
        tf.close()
        cookie_file = tf.name

        ydl_opts = {
            'cookiefile': cookie_file,
            'quiet': True, 'no_warnings': True, 'skip_download': True,
            'format': 'all'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        duration = info.get('duration', 0)
        formats = info.get('formats', [])
        
        # ฟังก์ชันคำนวณขนาดไฟล์จาก Bitrate กรณี YouTube ไม่ส่งขนาดไฟล์ตรงๆ มาให้
        def calc_size(fmt):
            size = fmt.get('filesize') or fmt.get('filesize_approx') or 0
            if not size and fmt.get('tbr') and duration:
                size = int((fmt.get('tbr') * 1000 / 8) * duration)
            return size

        # 1. หาขนาดไฟล์เสียงที่ดีที่สุด (Best Audio Size)
        audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
        best_audio_size = 0
        if audio_formats:
            best_audio = sorted(audio_formats, key=lambda x: x.get('tbr') or x.get('abr') or 0, reverse=True)[0]
            best_audio_size = calc_size(best_audio)

        seen_heights = set()
        video_options = []

        # 2. รวมขนาดภาพ + ขนาดเสียงเข้าด้วยกัน
        for f in formats:
            h = f.get('height')
            if h and h >= 144 and h not in seen_heights and f.get('vcodec') != 'none':
                seen_heights.add(h)
                v_size = calc_size(f)
                total_size = (v_size + best_audio_size) if v_size > 0 else 0
                
                video_options.append({
                    'resolution': f"{h}p",
                    'height': h,
                    'filesize': total_size
                })

        video_options = sorted(video_options, key=lambda x: x['height'], reverse=True)

        return jsonify({
            'title': info.get('title', 'YouTube Video'),
            'author': info.get('uploader') or info.get('channel', 'YouTube Creator'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': duration,
            'video_options': video_options,
            'audio_filesize': best_audio_size,
            'original_url': url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cookie_file and os.path.exists(cookie_file):
            os.unlink(cookie_file)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"เปิดเซิร์ฟเวอร์แล้ว กำลังรันอยู่ที่พอร์ต {port}")
    app.run(host='0.0.0.0', port=port)
