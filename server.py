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
# ฟังก์ชันช่วยเตรียม Cookie (แก้ไขปัญหา Newline บน Render)
# ==========================================
def create_temp_cookie_file():
    cookie_content = os.environ.get('YOUTUBE_COOKIE_CONTENT', '') or os.environ.get('COOKIE_CONTENT', '')
    if not cookie_content or len(cookie_content.strip()) <= 20:
        return None

    # แปลงตัวอักษร '\n' ที่ Render แปลงผิด ให้กลับเป็นบรรทัดใหม่จริง
    if '\\n' in cookie_content:
        cookie_content = cookie_content.replace('\\n', '\n')

    tf = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8')
    tf.write(cookie_content)
    tf.close()
    return tf.name


# ==========================================
# 1. API ดึงข้อมูลวิดีโอ
# ==========================================
@app.route('/api/get_youtube_video', methods=['POST'])
def get_youtube_video():
    data = request.json or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'กรุณาระบุ URL'}), 400

    if '?si=' in url: url = url.split('?si=')[0]
    if '&si=' in url: url = url.split('&si=')[0]

    cookie_file = create_temp_cookie_file()
    if not cookie_file:
        return jsonify({'error': 'กรุณาตั้งค่า YOUTUBE_COOKIE_CONTENT ใน Render Environment'}), 400

    try:
        ydl_opts = {
            'cookiefile': cookie_file,
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'format': 'all',
            'extractor_args': {
                'youtube': {
                    # ใช้ mweb และ android บน Render เพื่อหลบ Bot Verification บน Cloud IP
                    'player_client': ['mweb', 'android', 'ios']
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get('formats', [])
        seen_heights = set()
        video_options = []

        for f in formats:
            h = f.get('height')
            if h and h >= 144 and h not in seen_heights and f.get('vcodec') != 'none':
                seen_heights.add(h)
                video_options.append({
                    'resolution': f"{h}p",
                    'height': h
                })

        video_options = sorted(video_options, key=lambda x: x['height'], reverse=True)

        return jsonify({
            'title': info.get('title', 'YouTube Video'),
            'author': info.get('uploader') or info.get('channel', 'YouTube Creator'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'video_options': video_options,
            'original_url': url
        })
    except Exception as e:
        return jsonify({'error': f"ไม่สามารถดึงข้อมูลได้: {str(e)}"}), 500
    finally:
        if cookie_file and os.path.exists(cookie_file):
            os.unlink(cookie_file)


# ==========================================
# 2. API ดาวน์โหลดและประกอบไฟล์ด้วย FFmpeg
# ==========================================
@app.route('/api/download_local', methods=['GET'])
def download_local():
    url = request.args.get('url')
    res = request.args.get('res', '1080')
    is_audio = request.args.get('audio') == 'true'

    if not url:
        return "กรุณาระบุ URL", 400

    cookie_file = create_temp_cookie_file()

    download_dir = os.path.join(app.root_path, 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    for f in os.listdir(download_dir):
        try: os.remove(os.path.join(download_dir, f))
        except: pass

    outtmpl = os.path.join(download_dir, '%(title)s.%(ext)s')

    extractor_args = {
        'youtube': {
            'player_client': ['mweb', 'android', 'ios']
        }
    }

    if is_audio:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'cookiefile': cookie_file,
            'extractor_args': extractor_args,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True,
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={res}]+bestaudio/best',
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'cookiefile': cookie_file,
            'extractor_args': extractor_args,
            'quiet': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_audio:
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            else:
                filename = filename.rsplit('.', 1)[0] + '.mp4'
                
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {str(e)}", 500
    finally:
        if cookie_file and os.path.exists(cookie_file):
            os.unlink(cookie_file)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"เปิดเซิร์ฟเวอร์แล้ว กำลังรันอยู่ที่พอร์ต {port}")
    app.run(host='0.0.0.0', port=port)