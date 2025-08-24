#!/usr/bin/env python3
"""
Simple Web-based Steganography Suite - With file download capability
"""
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import base64
from io import BytesIO
from PIL import Image
import tempfile
import json
import uuid
from datetime import datetime

# Add current directory to path to import your modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your steganography functions
try:
    from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
    from stego.advanced_stego import encode_data_into_image, decode_data_from_image, get_image_capacity, analyze_stego_security
    print("✅ Steganography modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"📁 Output directory: {OUTPUT_DIR}")

# HTML Template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Steganography Suite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px; 
        }
        .container { 
            max-width: 800px; margin: 0 auto; background: white;
            border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden; 
        }
        header { 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white; padding: 30px; text-align: center; 
        }
        .tabs { display: flex; background: #f8f9fa; border-bottom: 2px solid #e9ecef; }
        .tab-btn { 
            flex: 1; padding: 15px; border: none; background: none; cursor: pointer;
            font-size: 16px; font-weight: 600; transition: all 0.3s ease; 
        }
        .tab-btn.active { background: #3498db; color: white; }
        .tab-content { padding: 30px; display: none; }
        .tab-content.active { display: block; }
        .upload-area { 
            border: 2px dashed #3498db; border-radius: 10px; padding: 40px;
            text-align: center; margin-bottom: 20px; cursor: pointer;
            transition: all 0.3s ease; 
        }
        .upload-area:hover { background: #f0f8ff; }
        .form-group { margin-bottom: 20px; }
        .btn-primary { 
            width: 100%; padding: 15px; background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white; border: none; border-radius: 8px; font-size: 18px; cursor: pointer;
            margin: 10px 0; transition: all 0.3s ease;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3); }
        .btn-download {
            padding: 12px 20px; background: #27ae60; color: white; border: none;
            border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block;
            margin: 10px 5px; transition: all 0.3s ease;
        }
        .btn-download:hover { background: #219a52; transform: translateY(-1px); }
        .result { 
            margin-top: 30px; padding: 20px; background: #f8f9fa; 
            border-radius: 10px; border-left: 4px solid #3498db;
        }
        .success { border-left-color: #27ae60; background: #e8f5e8; }
        .error { border-left-color: #e74c3c; background: #fde8e8; }
        .file-info { 
            background: white; padding: 15px; border-radius: 8px;
            margin: 10px 0; border: 1px solid #ddd;
        }
        .hidden { display: none; }
        .loading { opacity: 0.7; pointer-events: none; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 Advanced Steganography Suite</h1>
            <p>Hide secret messages in images with military-grade encryption</p>
        </header>

        <div class="tabs">
            <button class="tab-btn active" onclick="openTab('encode')">🔼 Encode</button>
            <button class="tab-btn" onclick="openTab('decode')">🔽 Decode</button>
            <button class="tab-btn" onclick="openTab('files')">📁 My Files</button>
        </div>

        <div id="encode" class="tab-content active">
            <div class="upload-area" onclick="document.getElementById('encodeImage').click()">
                <p>📁 Click to select carrier image (PNG/BMP)</p>
                <input type="file" id="encodeImage" accept=".png,.bmp" hidden>
                <div id="encodePreview"></div>
            </div>

            <div class="form-group">
                <label><strong>Secret Message:</strong></label>
                <textarea id="secretMessage" placeholder="Enter your secret message here..." 
                         style="width: 100%; height: 100px; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px;"></textarea>
            </div>

            <div class="form-group">
                <label><strong>Password:</strong></label>
                <input type="password" id="encodePassword" placeholder="Enter encryption password" 
                      style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px;">
            </div>

            <div class="form-group">
                <label><strong>Output Filename:</strong></label>
                <input type="text" id="outputFilename" placeholder="stego_image" 
                      style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px;">
                <small>Will be saved as: <span id="filenamePreview">stego_image.png</span></small>
            </div>

            <button class="btn-primary" onclick="encodeImage()">🚀 Encode Message</button>
            
            <div class="result hidden" id="encodeResult">
                <h3>✅ Encoding Successful!</h3>
                <div class="file-info">
                    <p><strong>Security Score:</strong> <span id="securityScore">0%</span></p>
                    <p><strong>File saved to:</strong> <span id="filePath">web_outputs/</span></p>
                    <p><strong>Message:</strong> <span id="resultMessage"></span></p>
                </div>
                <a id="downloadLink" class="btn-download" href="#" download>💾 Download Image</a>
                <button class="btn-download" onclick="openFileLocation()">📁 Open Folder</button>
            </div>

            <div class="result error hidden" id="encodeError">
                <h3>❌ Encoding Failed</h3>
                <p id="errorMessage"></p>
            </div>
        </div>

        <div id="decode" class="tab-content">
            <div class="upload-area" onclick="document.getElementById('decodeImage').click()">
                <p>📁 Click to select stego image (PNG)</p>
                <input type="file" id="decodeImage" accept=".png,.bmp" hidden>
                <div id="decodePreview"></div>
            </div>

            <div class="form-group">
                <label><strong>Password:</strong></label>
                <input type="password" id="decodePassword" placeholder="Enter decryption password" 
                      style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px;">
            </div>

            <button class="btn-primary" onclick="decodeImage()">🔍 Decode Message</button>
            
            <div class="result success hidden" id="decodeResult">
                <h3>✅ Decoding Successful!</h3>
                <div class="file-info">
                    <p><strong>Decoded Message:</strong></p>
                    <textarea id="decodedMessage" readonly 
                             style="width: 100%; height: 100px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background: #f9f9f9;"></textarea>
                </div>
                <button class="btn-download" onclick="copyToClipboard()">📋 Copy Message</button>
                <button class="btn-download" onclick="saveDecodedMessage()">💾 Save as Text File</button>
            </div>

            <div class="result error hidden" id="decodeError">
                <h3>❌ Decoding Failed</h3>
                <p id="decodeErrorMessage"></p>
            </div>
        </div>

        <div id="files" class="tab-content">
            <h3>📁 Recently Created Files</h3>
            <div class="file-info">
                <p><strong>Output Directory:</strong> <code id="outputDirPath">web_outputs/</code></p>
                <p><strong>Full Path:</strong> <code id="fullOutputPath"></code></p>
            </div>
            <button class="btn-primary" onclick="refreshFileList()">🔄 Refresh File List</button>
            <button class="btn-download" onclick="openFileLocation()">📁 Open Output Folder</button>
            
            <div id="fileList" style="margin-top: 20px;">
                <p>No files found yet. Encode some messages to see them here!</p>
            </div>
        </div>
    </div>

    <script> 
                let currentEncodedFile = '';
        let currentDecodedMessage = '';

        // Initialize tabs on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Show encode tab by default
            openTab('encode');
            
            // Set up file previews
            document.getElementById('encodeImage').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('encodePreview').innerHTML = 
                            `<img src="${e.target.result}" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 10px;">`;
                    };
                    reader.readAsDataURL(file);
                }
            });

            document.getElementById('decodeImage').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('decodePreview').innerHTML = 
                            `<img src="${e.target.result}" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 10px;">`;
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Update filename preview
            document.getElementById('outputFilename').addEventListener('input', function() {
                const filename = this.value.trim() || 'stego_image';
                document.getElementById('filenamePreview').textContent = filename + '.png';
            });
        });

        function openTab(tabName) {
            console.log('Opening tab:', tabName);
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
                tab.classList.remove('active');
            });
            
            // Remove active class from all buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show the selected tab and activate its button
            const tabElement = document.getElementById(tabName);
            if (tabElement) {
                tabElement.style.display = 'block';
                tabElement.classList.add('active');
            }
            
            // Activate the clicked button
            event.currentTarget.classList.add('active');
            
            // Special actions for specific tabs
            if (tabName === 'files') {
                refreshFileList();
                updatePathInfo();
            }
        }

        async function encodeImage() {
            const fileInput = document.getElementById('encodeImage');
            const message = document.getElementById('secretMessage').value;
            const password = document.getElementById('encodePassword').value;
            const filename = document.getElementById('outputFilename').value.trim() || 'stego_image';

            // Hide previous results
            document.getElementById('encodeResult').classList.add('hidden');
            document.getElementById('encodeError').classList.add('hidden');

            if (!fileInput.files[0]) {
                showError('Please select an image first');
                return;
            }
            if (!message) {
                showError('Please enter a secret message');
                return;
            }
            if (!password) {
                showError('Please enter a password');
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('message', message);
            formData.append('password', password);
            formData.append('filename', filename);

            try {
                document.body.classList.add('loading');
                const response = await fetch('/api/encode', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentEncodedFile = data.filename;
                    document.getElementById('securityScore').textContent = (data.security_score * 100).toFixed(1) + '%';
                    document.getElementById('filePath').textContent = 'web_outputs/' + data.filename;
                    document.getElementById('resultMessage').textContent = data.message;
                    
                    // Update download link
                    const downloadLink = document.getElementById('downloadLink');
                    downloadLink.href = '/download/' + data.filename;
                    downloadLink.download = data.filename;
                    
                    document.getElementById('encodeResult').classList.remove('hidden');
                    refreshFileList(); // Update file list
                } else {
                    showError('Error: ' + data.error);
                }
            } catch (error) {
                showError('Encoding failed: ' + error.message);
            } finally {
                document.body.classList.remove('loading');
            }
        }

        async function decodeImage() {
            const fileInput = document.getElementById('decodeImage');
            const password = document.getElementById('decodePassword').value;

            // Hide previous results
            document.getElementById('decodeResult').classList.add('hidden');
            document.getElementById('decodeError').classList.add('hidden');

            if (!fileInput.files[0]) {
                showDecodeError('Please select an image first');
                return;
            }
            if (!password) {
                showDecodeError('Please enter the password');
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('password', password);

            try {
                document.body.classList.add('loading');
                const response = await fetch('/api/decode', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentDecodedMessage = data.message;
                    document.getElementById('decodedMessage').value = data.message;
                    document.getElementById('decodeResult').classList.remove('hidden');
                } else {
                    showDecodeError('Error: ' + data.error);
                }
            } catch (error) {
                showDecodeError('Decoding failed: ' + error.message);
            } finally {
                document.body.classList.remove('loading');
            }
        }

        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('encodeError').classList.remove('hidden');
        }

        function showDecodeError(message) {
            document.getElementById('decodeErrorMessage').textContent = message;
            document.getElementById('decodeError').classList.remove('hidden');
        }

        function copyToClipboard() {
            navigator.clipboard.writeText(currentDecodedMessage).then(() => {
                alert('Message copied to clipboard!');
            });
        }

        function saveDecodedMessage() {
            const blob = new Blob([currentDecodedMessage], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'decoded_message.txt';
            a.click();
            URL.revokeObjectURL(url);
        }

        async function refreshFileList() {
            try {
                const response = await fetch('/api/files');
                const files = await response.json();
                
                const fileList = document.getElementById('fileList');
                if (files.length === 0) {
                    fileList.innerHTML = '<p>No files found yet. Encode some messages to see them here!</p>';
                    return;
                }
                
                fileList.innerHTML = files.map(file => `
                    <div class="file-info" style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <strong>${file.name}</strong> (${file.size})
                        <div style="margin-top: 5px;">
                            <a href="/download/${file.name}" class="btn-download" download>💾 Download</a>
                            <button class="btn-download" onclick="deleteFile('${file.name}')">🗑️ Delete</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error refreshing file list:', error);
            }
        }

        function updatePathInfo() {
            document.getElementById('outputDirPath').textContent = 'web_outputs/';
            document.getElementById('fullOutputPath').textContent = window.location.origin + '/web_outputs/';
        }

        function openFileLocation() {
            // This will open the output directory in a new tab
            window.open('/web_outputs/', '_blank');
        }

        async function deleteFile(filename) {
            if (confirm(`Are you sure you want to delete ${filename}?`)) {
                try {
                    const response = await fetch(`/api/delete/${filename}`, { method: 'DELETE' });
                    if (response.ok) {
                        refreshFileList();
                    } else {
                        alert('Failed to delete file');
                    }
                } catch (error) {
                    alert('Error deleting file: ' + error.message);
                }
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/encode', methods=['POST'])
def encode():
    try:
        image_file = request.files['image']
        message = request.form['message']
        password = request.form['password']
        filename = request.form.get('filename', 'stego_image').strip()
        
        # Ensure filename ends with .png
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        # Clean filename (remove special characters)
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        filename = filename.replace(' ', '_') + '.png'
        
        # Create full output path
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as input_tmp:
            image_file.save(input_tmp.name)
            input_path = input_tmp.name
        
        # Encode the message
        result = encode_data_into_image(
            input_path, message.encode(), password, output_path,
            lsb_bits=2, use_compression=True
        )
        
        # Clean up temporary file
        os.unlink(input_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': filename,
                'message': result.get('message', ''),
                'security_score': result.get('security_score', 0),
                'file_path': output_path
            })
        else:
            # Clean up output file if encoding failed
            if os.path.exists(output_path):
                os.unlink(output_path)
            return jsonify({'success': False, 'error': result.get('error', 'Encoding failed')})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/decode', methods=['POST'])
def decode():
    try:
        image_file = request.files['image']
        password = request.form['password']
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image_file.save(tmp.name)
            input_path = tmp.name
        
        # Decode the message
        result = decode_data_from_image(input_path, password, 2)
        
        # Clean up
        os.unlink(input_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['data'].decode('utf-8')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Decoding failed')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files')
def list_files():
    try:
        files = []
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.png'):
                filepath = os.path.join(OUTPUT_DIR, filename)
                size = os.path.getsize(filepath)
                files.append({
                    'name': filename,
                    'size': f"{size / 1024:.1f} KB",
                    'path': filepath
                })
        return jsonify(files)
    except Exception as e:
        return jsonify([])

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/web_outputs/')
def serve_outputs_directory():
    """Serve the output directory for easy access"""
    files = []
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith('.png'):
            filepath = os.path.join(OUTPUT_DIR, filename)
            size = os.path.getsize(filepath)
            files.append(f'<li><a href="/download/{filename}" download>{filename}</a> ({size/1024:.1f} KB)</li>')
    
    return f"""
    <html><body>
        <h1>Web Outputs Directory</h1>
        <p>Path: {OUTPUT_DIR}</p>
        <ul>{''.join(files)}</ul>
        <p><a href="/">← Back to Steganography Suite</a></p>
    </body></html>
    """

if __name__ == '__main__':
    print("🚀 Starting Advanced Steganography Web Suite...")
    print("📁 Output files will be saved to:", OUTPUT_DIR)
    print("🌐 Open: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)