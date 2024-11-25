from flask import Flask, request, jsonify, render_template_string, send_file
import os
from datetime import datetime

app = Flask(__name__)

# Directory to save received images
SAVE_DIR = "/Users/kirthika/Desktop/img"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route('/receive', methods=['POST'])
def receive_image():
    """Endpoint to receive images sent by the sender."""
    if 'image' in request.files:
        image = request.files['image']
        # Generate a timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
        filename = f"{SAVE_DIR}/image_{timestamp}.jpg"
        # Save the image
        image.save(filename)
        print(f"Image received and saved as {filename}")
        return jsonify({"message": "Image received successfully", "filename": filename}), 200
    return jsonify({"error": "No image received"}), 400

@app.route('/latest-image')
def latest_image():
    """Serve the latest received image."""
    try:
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.jpg')]
        if files:
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(SAVE_DIR, x)))
            return send_file(os.path.join(SAVE_DIR, latest_file), mimetype='image/jpeg')
        return "No images available", 404
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    """Home route with buttons for triggering /a1 and /a2 and showing the latest image."""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Receiver Flask Server</title>
        <script>
            function sendRequest(endpoint) {
                fetch(endpoint)
                    .then(response => response.json())
                    .then(data => alert(JSON.stringify(data)))
                    .catch(err => alert("Error: " + err));
            }

            function refreshImage() {
                const imgFrame = document.getElementById("image-frame");
                imgFrame.src = "/latest-image?" + new Date().getTime(); // Add timestamp to avoid caching
            }

            setInterval(refreshImage, 5000); // Refresh the image every 5 seconds
        </script>
    </head>
    <body>
        <h1>Receiver Flask Server</h1>
        <p>Endpoints:</p>
        <ul>
            <li>
                <button onclick="sendRequest('/a1')">Request /a1</button>
            </li>
            <li>
                <button onclick="sendRequest('/a2')">Request /a2</button>
            </li>
        </ul>
        <h2>Latest Image:</h2>
        <img id="image-frame" src="/latest-image" alt="Latest image will appear here" style="max-width: 100%; border: 1px solid black;">
    </body>
    </html>
    ''')

@app.route('/a1', methods=['GET'])
def trigger_a1():
    """Trigger /a1 on the sender server."""
    sender_ip = "http://127.0.0.1:5050"  # Sender Flask app's IP address
    response = os.system(f"curl {sender_ip}/a1")
    return jsonify({"message": f"Triggered /a1 on sender", "status": response})

@app.route('/a2', methods=['GET'])
def trigger_a2():
    """Trigger /a2 on the sender server."""
    sender_ip = "http://127.0.0.1:5050"  # Sender Flask app's IP address
    response = os.system(f"curl {sender_ip}/a2")
    return jsonify({"message": f"Triggered /a2 on sender", "status": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7770)