from flask import Flask, jsonify, request
import threading
import time
import cv2
import numpy as np
import urllib.request
import requests

app = Flask(__name__)

# URLs for the ESP32-CAM modules
ESP32_CAM_1_URL = "http://192.168.222.43/cam-hi.jpg"
ESP32_CAM_2_URL = "http://192.168.222.43/cam-hi.jpg"

def fetch_frame(cam_url):
    """Fetch a single frame from the ESP32-CAM."""
    try:
        img_resp = urllib.request.urlopen(cam_url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    except Exception as e:
        print(f"Error fetching frame: {e}")
        return None

def send_frames(cam_url, client_ip, duration=120, interval=5):
    """Send frames to the requesting client for the specified duration."""
    end_time = time.time() + duration
    while time.time() < end_time:
        frame = fetch_frame(cam_url)
        if frame:
            try:
                response = requests.post(
                    f"http://{client_ip}:7770/receive",  # Adjust port to receiver's
                    files={"image": ("frame.jpg", frame, "image/jpeg")}
                )
                print(f"Sent frame to {client_ip}: {response.status_code}")
            except Exception as e:
                print(f"Error sending frame: {e}")
        time.sleep(interval)

@app.route('/a1', methods=['GET'])
def handle_a1():
    """Handle requests for ESP32-CAM 1."""
    client_ip = request.remote_addr
    threading.Thread(target=send_frames, args=(ESP32_CAM_1_URL, client_ip)).start()
    return jsonify({"message": "Streaming frames from ESP32-CAM 1 to client", "client_ip": client_ip})

@app.route('/a2', methods=['GET'])
def handle_a2():
    """Handle requests for ESP32-CAM 2."""
    client_ip = request.remote_addr
    threading.Thread(target=send_frames, args=(ESP32_CAM_2_URL, client_ip)).start()
    return jsonify({"message": "Streaming frames from ESP32-CAM 2 to client", "client_ip": client_ip})

@app.route('/')
def home():
    """Home route to list endpoints."""
    return '''
    <h1>ESP32-CAM Flask Server</h1>
    <p>Endpoints:</p>
    <ul>
        <li><a href="/a1">/a1</a> - Send frames from ESP32-CAM 1</li>
        <li><a href="/a2">/a2</a> - Send frames from ESP32-CAM 2</li>
    </ul>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)