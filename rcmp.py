from flask import Flask, request, jsonify, render_template_string, send_file
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Directories to save images from ESP32-CAM 1 and ESP32-CAM 2
SAVE_DIR_A1 = "/Users/kirthika/Desktop/img/a1"
SAVE_DIR_A2 = "/Users/kirthika/Desktop/img/a2"
os.makedirs(SAVE_DIR_A1, exist_ok=True)
os.makedirs(SAVE_DIR_A2, exist_ok=True)

# Sender Flask server URL
SENDER_URL = "http://127.0.0.1:5050"  # Replace with the actual sender Flask server URL and port

@app.route('/receive', methods=['POST'])
def receive_image():
    """Receive images from the sender."""
    if 'image' in request.files and 'cam' in request.form:
        image = request.files['image']
        camera = request.form['cam']  # Get the camera identifier (a1 or a2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')

        # Save the image in the appropriate directory
        if camera == "a1":
            save_dir = SAVE_DIR_A1
        elif camera == "a2":
            save_dir = SAVE_DIR_A2
        else:
            return jsonify({"error": "Invalid camera identifier"}), 400

        filename = f"{save_dir}/image_{timestamp}.jpg"
        image.save(filename)
        print(f"Image received from {camera} and saved as {filename}")
        return jsonify({"message": "Image received successfully", "filename": filename}), 200

    return jsonify({"error": "Invalid request"}), 400

@app.route('/latest-image-a1')
def latest_image_a1():
    """Serve the latest image from ESP32-CAM 1."""
    return _serve_latest_image(SAVE_DIR_A1)

@app.route('/latest-image-a2')
def latest_image_a2():
    """Serve the latest image from ESP32-CAM 2."""
    return _serve_latest_image(SAVE_DIR_A2)

def _serve_latest_image(directory):
    """Serve the latest image from the specified directory."""
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.jpg')]
        if files:
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(directory, x)))
            return send_file(os.path.join(directory, latest_file), mimetype='image/jpeg')
        return "No images available", 404
    except Exception as e:
        return str(e), 500

@app.route('/a1', methods=['GET'])
def trigger_a1():
    """Trigger the sender Flask server to stream from ESP32-CAM 1."""
    try:
        response = requests.get(f"{SENDER_URL}/a1")  # Make a GET request to the sender's /a1 endpoint
        return jsonify({"message": "Triggered ESP32-CAM 1 streaming", "response": response.json()})
    except Exception as e:
        return jsonify({"error": f"Failed to trigger ESP32-CAM 1: {str(e)}"}), 500

@app.route('/a2', methods=['GET'])
def trigger_a2():
    """Trigger the sender Flask server to stream from ESP32-CAM 2."""
    try:
        response = requests.get(f"{SENDER_URL}/a2")  # Make a GET request to the sender's /a2 endpoint
        return jsonify({"message": "Triggered ESP32-CAM 2 streaming", "response": response.json()})
    except Exception as e:
        return jsonify({"error": f"Failed to trigger ESP32-CAM 2: {str(e)}"}), 500

@app.route('/')
def home():
    """Display the latest images and buttons for triggering requests."""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Receiver Flask Server</title>
        <script>
            function sendRequest(endpoint) {
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => alert(JSON.stringify(data)))
                    .catch(err => alert("Error: " + err));
            }

            function refreshImages() {
                document.getElementById("image-a1").src = "/latest-image-a1?" + new Date().getTime();
                document.getElementById("image-a2").src = "/latest-image-a2?" + new Date().getTime();
            }
            setInterval(refreshImages, 1000); // Refresh images every second
        </script>
    </head>
    <body>
        <h1>Receiver Flask Server</h1>
        <button onclick="sendRequest('/a1')">Request from ESP32-CAM 1 (A1)</button>
        <button onclick="sendRequest('/a2')">Request from ESP32-CAM 2 (A2)</button>
        <h2>Latest Images:</h2>
        <div>
            <h3>ESP32-CAM 1</h3>
            <img id="image-a1" src="/latest-image-a1" alt="Latest image from A1" style="max-width: 100%; border: 1px solid black;">
        </div>
        <div>
            <h3>ESP32-CAM 2</h3>
            <img id="image-a2" src="/latest-image-a2" alt="Latest image from A2" style="max-width: 100%; border: 1px solid black;">
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7770)
