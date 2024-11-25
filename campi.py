from flask import Flask, Response
import cv2
import numpy as np
import urllib.request

app = Flask(__name__)

# URLs for the ESP32-CAM modules
ESP32_CAM_1_URL = "http://192.168.222.43/cam-hi.jpg"
ESP32_CAM_2_URL = "http://192.168.222.43/cam-hi.jpg"

def generate_frames(cam_url):
    """Generator function to fetch and yield frames from the ESP32-CAM"""
    while True:
        try:
            # Fetch the image from the ESP32-CAM
            img_resp = urllib.request.urlopen(cam_url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgnp, -1)

            # Encode the frame in JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield the frame bytes in the required format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error fetching frames: {e}")
            break

@app.route('/a1', methods=['GET'])
def stream_from_cam1():
    """Stream from ESP32-CAM 1"""
    return Response(generate_frames(ESP32_CAM_1_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/a2', methods=['GET'])
def stream_from_cam2():
    """Stream from ESP32-CAM 2"""
    return Response(generate_frames(ESP32_CAM_2_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def home():
    """Home route to list endpoints"""
    return '''
    <h1>ESP32-CAM Flask Server</h1>
    <p>Endpoints:</p>
    <ul>
        <li><a href="/a1">/a1</a> - Stream from ESP32-CAM 1</li>
        <li><a href="/a2">/a2</a> - Stream from ESP32-CAM 2</li>
    </ul>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
