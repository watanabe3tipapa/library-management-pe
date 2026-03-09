import cv2
from pyzbar import pyzbar
import time
import re
import csv
import os
import threading
import argparse
from flask import Flask, render_template_string, Response, request, jsonify

DEFAULT_CSV = "scanned_isbn.csv"

def normalize_isbn(code: str) -> str | None:
    digits = re.sub(r'[^0-9Xx]', '', code)
    if len(digits) == 13:
        return digits
    if len(digits) == 10:
        core = '978' + digits[:-1]
        total = 0
        for i, ch in enumerate(core):
            n = int(ch)
            total += n if i % 2 == 0 else 3 * n
        check = (10 - (total % 10)) % 10
        return core + str(check)
    return None

def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    results = []
    for b in barcodes:
        data = b.data.decode('utf-8')
        typ = b.type
        results.append((typ, data, b.rect))
    return results

app = Flask(__name__)

scanned_isbns = []
seen = {}
cap = None
lock = threading.Lock()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISBNスキャナー</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 20px; color: #333; }
        .main { display: flex; gap: 20px; }
        .video-section { flex: 1; background: #000; border-radius: 8px; overflow: hidden; }
        .video-section img { width: 100%; display: block; }
        .list-section { flex: 0 0 350px; background: #fff; border-radius: 8px; padding: 15px; }
        .list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .list-header h2 { font-size: 16px; }
        .count { color: #666; font-size: 14px; }
        #isbn-list { list-style: none; max-height: 400px; overflow-y: auto; border: 1px solid #eee; border-radius: 4px; }
        #isbn-list li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        #isbn-list li:last-child { border-bottom: none; }
        #isbn-list li:hover { background: #f9f9f9; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-save { background: #4CAF50; color: white; }
        .btn-clear { background: #f44336; color: white; }
        .btn-download { background: #2196F3; color: white; }
        button:hover { opacity: 0.9; }
        .status { text-align: center; padding: 10px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 ISBNスキャナー</h1>
        <div class="main">
            <div class="video-section">
                <img src="{{ url_for('video_feed') }}" id="video">
            </div>
            <div class="list-section">
                <div class="list-header">
                    <h2>スキャン済みISBN</h2>
                    <span class="count" id="count">件数: 0</span>
                </div>
                <ul id="isbn-list"></ul>
                <div class="btn-group">
                    <button class="btn-save" onclick="saveList()">保存</button>
                    <button class="btn-clear" onclick="clearList()">クリア</button>
                    <button class="btn-download" onclick="downloadCSV()">ダウンロード</button>
                </div>
                <p class="status" id="status">カメラ起動中...</p>
            </div>
        </div>
    </div>
    <script>
        let isbns = [];
        
        function updateList() {
            fetch('/get_isbns')
                .then(r => r.json())
                .then(data => {
                    isbns = data;
                    const list = document.getElementById('isbn-list');
                    list.innerHTML = isbns.map(isbn => `<li><span>${isbn}</span></li>`).join('');
                    document.getElementById('count').textContent = '件数: ' + isbns.length;
                });
        }
        
        function saveList() {
            fetch('/save_csv', { method: 'POST' })
                .then(r => r.json())
                .then(data => alert(data.message));
        }
        
        function clearList() {
            fetch('/clear_isbns', { method: 'POST' })
                .then(() => updateList());
        }
        
        function downloadCSV() {
            window.location.href = '/download_csv';
        }
        
        setInterval(updateList, 1000);
        
        document.getElementById('video').onload = function() {
            document.getElementById('status').textContent = 'スキャン中... (qで終了)';
        };
    </script>
</body>
</html>
'''

def gen_frames():
    global cap, seen
    while True:
        if cap is None or not cap.isOpened():
            break
        ret, frame = cap.read()
        if not ret:
            break
        
        barcodes = read_barcodes(frame)
        for typ, data, rect in barcodes:
            isbn = normalize_isbn(data)
            if isbn:
                now = time.time()
                last_time = seen.get(isbn, 0)
                if now - last_time > 2:
                    print(isbn)
                    with lock:
                        if isbn not in scanned_isbns:
                            scanned_isbns.append(isbn)
                    seen[isbn] = now
                x, y, w, h = rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, isbn, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_isbns')
def get_isbns():
    with lock:
        return jsonify(scanned_isbns.copy())

@app.route('/save_csv', methods=['POST'])
def save_csv():
    with lock:
        with open(DEFAULT_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            for isbn in scanned_isbns:
                writer.writerow([isbn])
    return jsonify({"message": f"保存しました: {DEFAULT_CSV}"})

@app.route('/clear_isbns', methods=['POST'])
def clear_isbns():
    global seen
    with lock:
        scanned_isbns.clear()
        seen.clear()
    return jsonify({"message": "クリアしました"})

@app.route('/download_csv')
def download_csv():
    with lock:
        temp_csv = "temp_download.csv"
        with open(temp_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            for isbn in scanned_isbns:
                writer.writerow([isbn])
    
    def generate():
        with open(temp_csv, 'r') as f:
            yield from f
        os.remove(temp_csv)
    
    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=scanned_isbn.csv'})

def main():
    global cap, DEFAULT_CSV
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default=DEFAULT_CSV, help="出力CSVファイル名")
    args = parser.parse_args()
    
    DEFAULT_CSV = args.output
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラを開けませんでした")
        return
    
    print("ブラウザで http://localhost:5005 を開いてください")
    app.run(threaded=True, port=5005)

if __name__ == '__main__':
    main()
