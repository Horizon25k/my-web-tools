from flask import Flask, request, jsonify, send_file
import os
import tempfile
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) # อนุญาตให้หน้าเว็บ HTML เรียกใช้ API นี้ได้
# กำหนดให้เข้าลิงก์หลัก (/) แล้วแสดงหน้า index.html
@app.route('/', methods=['GET'])
def home():
    return send_file('index.html')

# กำหนดเส้นทางสำหรับหน้าดาวน์โหลด
@app.route('/x-downloader.html', methods=['GET'])
def x_downloader_page():
    return send_file('x-downloader.html')

@app.route('/webp_pdf.html', methods=['GET'])
def webp_pdf_page():
    return send_file('webp_pdf.html')

@app.route('/tiktok-downloader.html', methods=['GET'])
def tiktok_downloader_page():
    return send_file('tiktok-downloader.html')

@app.route('/api/get_x_video', methods=['POST'])
def get_x_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'กรุณาส่งลิงก์มาด้วย'}), 400

    # ดึงค่าคุกกี้ที่ซ่อนไว้ใน Environment Variables ของ Cloud มาสร้างเป็นไฟล์ชั่วคราว
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
        'skip_download': True # สั่งแค่ดึงลิงก์ ไม่ต้องโหลดไฟล์ลงเครื่องเซิร์ฟเวอร์
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
            
            # คัดกรองหาไฟล์ MP4 ที่ความละเอียดดีที่สุด
            formats = info.get('formats', [])
            mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
            
            # ลบไฟล์คุกกี้ชั่วคราวทิ้งหลังใช้งานเสร็จ (เพื่อความสะอาดและความปลอดภัย)
            if cookie_file_path and os.path.exists(cookie_file_path):
                os.unlink(cookie_file_path)

            if not mp4_formats:
                return jsonify({'error': 'ไม่พบไฟล์วิดีโอ'}), 404
                
            best_video = sorted(mp4_formats, key=lambda x: x.get('height', 0), reverse=True)[0]
            
            # ส่งข้อมูลกลับไปให้หน้าเว็บ HTML
            return jsonify({
                'author': info.get('uploader', 'Unknown'),
                'author_id': info.get('uploader_id', ''),
                'text': info.get('title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': best_video.get('url')
            })
            
    except Exception as e:
        # เผื่อเกิด Error ให้แน่ใจว่าลบไฟล์ชั่วคราวทิ้งด้วย
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.unlink(cookie_file_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # รองรับการรันบน Cloud (อ่านพอร์ตจากระบบ หรือใช้ 5000 ถ้าทดสอบบนเครื่องตัวเอง)
    port = int(os.environ.get('PORT', 5000))
    print(f"เปิดเซิร์ฟเวอร์หลังบ้านแล้ว! กำลังรันอยู่ที่พอร์ต {port}")
    app.run(host='0.0.0.0', port=port)