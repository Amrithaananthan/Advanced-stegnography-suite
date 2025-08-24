#!/usr/bin/env python3
"""
StegSecure Pro - Enhanced Web Steganography Suite with Functional Tabs and Proper UI Feedback
"""
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
    from stego.advanced_stego import encode_data_into_image, decode_data_from_image
    print("Steg modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Output directory: {OUTPUT_DIR}")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>StegSecure Pro</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
<style>
:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --background: #f8fafc;
  --card-bg: #fff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border: #e2e8f0;
  --success: #10b981;
  --danger: #ef4444;
  --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}
* { margin:0; padding:0; box-sizing:border-box; transition: all 0.3s ease; }
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: var(--background);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
nav {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}
nav .logo {
  font-weight: 700;
  color: var(--primary);
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
nav .logo i { font-size: 1.6rem; }
nav .tabs {
  display: flex;
  gap: 2rem;
}
nav .tab {
  cursor: pointer;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: var(--text-secondary);
  user-select: none;
}
nav .tab.active, nav .tab:hover {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary);
}
main {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
  flex-grow: 1;
}
.card {
  background: var(--card-bg);
  box-shadow: var(--shadow);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}
h2 {
  color: var(--primary);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
}
label {
  margin-bottom: 0.4rem;
  font-weight: 600;
}
input[type="file"] {
  display: none;
}
.upload-area {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--primary);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s ease;
}
.upload-area:hover {
  background-color: rgba(37, 99, 235, 0.15);
}
.image-preview img {
  max-width: 200px;
  max-height: 200px;
  margin-top: 1rem;
  border-radius: 8px;
  box-shadow: var(--shadow);
}
input[type="text"],
input[type="password"],
textarea {
  padding: 0.7rem 1rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 2px solid var(--border);
  background: var(--card-bg);
  color: var(--text-primary);
  resize: vertical;
}
input[type="text"]:focus,
input[type="password"]:focus,
textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}
textarea {
  min-height: 120px;
}
button.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
}
button.btn-primary:hover {
  background: var(--primary-dark);
}
a.btn-download, button.btn-download {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
a.btn-download {
  background: var(--success);
}
a.btn-download:hover {
  background: #0f9a58;
}
button.btn-download {
  background: var(--primary);
  border: none;
}
button.btn-download:hover {
  background: var(--primary-dark);
}
.result {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  background: var(--background);
  border-left: 6px solid var(--primary);
  box-shadow: var(--shadow);
  user-select: text;
}
.result.success {
  border-color: var(--success);
  background: #e6f4ea;
  color: var(--text-primary);
}
.result.error {
  border-color: var(--danger);
  background: #fbeaea;
  color: var(--text-primary);
}
.hidden {
  display: none !important;
}
#fileList {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 1rem;
}
.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95rem;
}
.file-info button,
.file-info a {
  font-weight: 400;
  font-size: 0.9rem;
}
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  color: white;
  font-weight: 600;
  font-size: 1.2rem;
  flex-direction: column;
}
.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
@media(max-width: 768px) {
  nav .tabs {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  .image-preview img {
    max-width: 100%;
    height: auto;
  }
}
</style>
</head>
<body>

<nav>
  <div class="logo"><i class="fas fa-lock"></i> StegSecure Pro</div>
  <div class="tabs" role="tablist">
    <div role="tab" aria-selected="true" tabindex="0" class="tab active" data-tab="encode">Encode</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="decode">Decode</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="files">My Files</div>
    <div role="tab" aria-selected="false" tabindex="-1" class="tab" data-tab="about">About</div>
  </div>
</nav>

<main>
  <section id="encode" class="card" role="tabpanel">
    <h2><i class="fas fa-lock"></i> Encode Secret Message</h2>
    <p>Hide your message securely within an image.</p>
    <div class="form-group">
      <label for="encodeImage">Carrier Image</label>
      <div class="upload-area" id="encodeUpload" tabindex="0" aria-label="Upload carrier image (PNG or BMP)">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop your image here or click to browse</p>
        <small>Supports PNG, BMP formats • Max 10MB</small>
        <input type="file" accept=".png,.bmp" id="encodeImage" aria-describedby="encodeImageDesc" />
      </div>
      <div id="encodePreview" class="image-preview" aria-live="polite"></div>
    </div>

    <div class="form-group">
      <label for="secretMessage">Secret Message</label>
      <textarea id="secretMessage" maxlength="10000" placeholder="Enter your secret message"></textarea>
    </div>

    <div class="form-group">
      <label for="encodePassword">Encryption Password</label>
      <input type="password" id="encodePassword" autocomplete="new-password" placeholder="Enter strong password" />
    </div>

    <div class="form-group">
      <label for="outputFilename">Output Filename</label>
      <input type="text" id="outputFilename" placeholder="secure_image" />
      <small>Will be saved as: <span id="filenamePreview">secure_image.png</span></small>
    </div>

    <button class="btn-primary" id="encodeBtn"><i class="fas fa-lock"></i> Encode Message</button>

    <div id="encodeResult" class="result success hidden" role="alert" aria-live="assertive">
      <h3>Encoding Successful!</h3>
      <p><strong>Security Score:</strong> <span id="securityScore">0%</span></p>
      <p><strong>File Size:</strong> <span id="fileSize">0 KB</span></p>
      <p><strong>Saved To:</strong> <span id="filePath">web_outputs/</span></p>
      <a id="downloadLink" href="#" download class="btn-download"><i class="fas fa-download"></i> Download Image</a>
      <button class="btn-download" id="openFolderBtn"><i class="fas fa-folder-open"></i> Open Folder</button>
    </div>

    <div id="encodeError" class="result error hidden" role="alert" aria-live="assertive">
      <h3>Encoding Failed</h3>
      <p id="errorMessage"></p>
    </div>
  </section>

  <section id="decode" class="card hidden" role="tabpanel" aria-hidden="true">
    <h2><i class="fas fa-unlock"></i> Decode Secret Message</h2>
    <p>Extract hidden messages from steganographic images.</p>
    <div class="form-group">
      <label for="decodeImage">Stego Image</label>
      <div class="upload-area" id="decodeUpload" tabindex="0" aria-label="Upload stego image (PNG or BMP)">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop stego image here or click to browse</p>
        <small>Supports PNG, BMP formats with hidden data</small>
        <input type="file" accept=".png,.bmp" id="decodeImage" />
      </div>
      <div id="decodePreview" class="image-preview" aria-live="polite"></div>
    </div>

    <div class="form-group">
      <label for="decodePassword">Decryption Password</label>
      <input type="password" id="decodePassword" autocomplete="current-password" placeholder="Enter decryption password" />
    </div>

    <button class="btn-primary" id="decodeBtn"><i class="fas fa-unlock"></i> Decode Message</button>

    <div id="decodeResult" class="result success hidden" role="alert" aria-live="assertive">
      <h3>Decoding Successful!</h3>
      <textarea id="decodedMessage" readonly rows="6" aria-label="Decoded message"></textarea>
      <div style="margin-top: 1rem;">
        <button class="btn-download" id="copyMessageBtn"><i class="fas fa-copy"></i> Copy Message</button>
        <button class="btn-download" id="saveMessageBtn"><i class="fas fa-save"></i> Save as Text File</button>
      </div>
    </div>

    <div id="decodeError" class="result error hidden" role="alert" aria-live="assertive">
      <h3>Decoding Failed</h3>
      <p id="decodeErrorMessage"></p>
    </div>
  </section>

  <section id="files" class="card hidden" role="tabpanel" aria-hidden="true">
    <h2><i class="fas fa-folder"></i> File Management</h2>
    <p>Manage your encoded images and outputs</p>
    <div style="margin-bottom: 1rem;">
      <button class="btn-primary" id="refreshFileListBtn"><i class="fas fa-sync"></i> Refresh File List</button>
      <button class="btn-download" id="openFilesFolderBtn"><i class="fas fa-folder-open"></i> Open Folder</button>
    </div>
    <div id="fileList" aria-live="polite" aria-relevant="additions removals"></div>
  </section>

  <section id="about" class="card hidden" role="tabpanel" aria-hidden="true">
    <h2><i class="fas fa-info-circle"></i> About StegSecure Pro</h2>
    <p>A professional-grade tool for secure information hiding using steganography and AES encryption.</p>
    <ul>
      <li><strong>Military-Grade Encryption:</strong> AES-256-GCM with secure key derivation</li>
      <li><strong>LSB Steganography:</strong> Hide data in image pixels with configurable stealth levels</li>
      <li><strong>Smart Compression:</strong> Optimize payload size using intelligent compression</li>
      <li><strong>Security Analysis:</strong> Real-time scoring and risk assessment</li>
    </ul>
  </section>
</main>

<div class="loading-overlay" id="loadingOverlay" aria-hidden="true">
  <div class="spinner" role="img" aria-label="Loading spinner"></div>
  Processing your request...
</div>

<script>
(() => {
  const tabs = document.querySelectorAll('nav .tab');
  const contents = {
    encode: document.getElementById('encode'),
    decode: document.getElementById('decode'),
    files: document.getElementById('files'),
    about: document.getElementById('about'),
  };

  const loadingOverlay = document.getElementById('loadingOverlay');

  function activateTab(tabName) {
    tabs.forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabName);
      tab.setAttribute('aria-selected', tab.dataset.tab === tabName ? 'true' : 'false');
      tab.tabIndex = tab.dataset.tab === tabName ? 0 : -1;
    });
    Object.entries(contents).forEach(([key, el]) => {
      const isActive = key === tabName;
      el.classList.toggle('hidden', !isActive);
      el.setAttribute('aria-hidden', !isActive);
      if (isActive) el.focus();
    });
  }
  tabs.forEach(tab => {
    tab.addEventListener('click', e => {
      e.preventDefault();
      activateTab(tab.dataset.tab);
    });
    tab.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        e.preventDefault();
        const index = Array.from(tabs).indexOf(e.target);
        let newIndex = e.key === 'ArrowRight' ? index + 1 : index - 1;
        if (newIndex < 0) newIndex = tabs.length - 1;
        if (newIndex >= tabs.length) newIndex = 0;
        tabs[newIndex].focus();
        activateTab(tabs[newIndex].dataset.tab);
      }
    });
  });
  activateTab('encode');

  // Drag and drop upload helpers
  function setupUploadArea(uploadAreaId, fileInputId, previewId) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    const preview = document.getElementById(previewId);

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', e => {
      e.preventDefault();
      uploadArea.style.backgroundColor = 'rgba(37, 99, 235, 0.15)';
    });
    uploadArea.addEventListener('dragleave', () => {
      uploadArea.style.backgroundColor = '';
    });
    uploadArea.addEventListener('drop', e => {
      e.preventDefault();
      uploadArea.style.backgroundColor = '';
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        previewFile(fileInput, preview);
      }
    });
    fileInput.addEventListener('change', () => previewFile(fileInput, preview));
  }
  function previewFile(input, preview) {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.innerHTML = `<img src="${e.target.result}" alt="Selected image preview" />`;
      };
      reader.readAsDataURL(file);
    }
  }
  setupUploadArea('encodeUpload', 'encodeImage', 'encodePreview');
  setupUploadArea('decodeUpload', 'decodeImage', 'decodePreview');

  // Output filename preview update
  document.getElementById('outputFilename').addEventListener('input', e => {
    const val = e.target.value.trim() || 'secure_image';
    document.getElementById('filenamePreview').textContent = val + '.png';
  });

  // Show / hide loading state
  function showLoading(state) {
    loadingOverlay.style.display = state ? 'flex' : 'none';
    document.body.style.pointerEvents = state ? 'none' : 'auto';
  }

  // Encode button event
  document.getElementById('encodeBtn').addEventListener('click', async () => {
    clearEncodeMessages();
    const fileInput = document.getElementById('encodeImage');
    const message = document.getElementById('secretMessage').value.trim();
    const password = document.getElementById('encodePassword').value;
    const filename = document.getElementById('outputFilename').value.trim() || 'secure_image';

    if (!fileInput.files[0]) return showEncodeError('Please select a carrier image.');
    if (!message) return showEncodeError('Please enter a secret message.');
    if (!password) return showEncodeError('Please enter an encryption password.');
    if (message.length > 10000) return showEncodeError('Message is too long (max 10,000 chars).');

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('message', message);
    formData.append('password', password);
    formData.append('filename', filename);

    showLoading(true);
    try {
      const res = await fetch('/api/encode', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) showEncodeSuccess(data);
      else showEncodeError(data.error || 'Encoding failed.');
    } catch (err) {
      showEncodeError('Encoding failed: ' + err.message);
    }
    showLoading(false);
  });
  function showEncodeSuccess(data) {
    document.getElementById('securityScore').textContent = (data.security_score * 100).toFixed(1) + '%';
    document.getElementById('fileSize').textContent = Math.round(data.encrypted_size / 1024) + ' KB';
    document.getElementById('filePath').textContent = 'web_outputs/' + data.filename;
    const link = document.getElementById('downloadLink');
    link.href = '/download/' + data.filename;
    link.download = data.filename;
    document.getElementById('encodeResult').classList.remove('hidden');
  }
  function showEncodeError(msg) {
    const err = document.getElementById('encodeError');
    err.querySelector('#errorMessage').textContent = msg;
    err.classList.remove('hidden');
  }
  function clearEncodeMessages() {
    document.getElementById('encodeResult').classList.add('hidden');
    document.getElementById('encodeError').classList.add('hidden');
  }

  // Decode button event
  document.getElementById('decodeBtn').addEventListener('click', async () => {
    clearDecodeMessages();
    const fileInput = document.getElementById('decodeImage');
    const password = document.getElementById('decodePassword').value;

    if (!fileInput.files[0]) return showDecodeError('Please select a stego image.');
    if (!password) return showDecodeError('Please enter decryption password.');

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('password', password);

    showLoading(true);
    try {
      const res = await fetch('/api/decode', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) showDecodeSuccess(data.message);
      else showDecodeError(data.error || 'Decoding failed.');
    } catch (err) {
      showDecodeError('Decoding failed: ' + err.message);
    }
    showLoading(false);
  });
  function showDecodeSuccess(message) {
    const area = document.getElementById('decodedMessage');
    area.value = message;
    document.getElementById('decodeResult').classList.remove('hidden');
  }
  function showDecodeError(msg) {
    const err = document.getElementById('decodeError');
    err.querySelector('#decodeErrorMessage').textContent = msg;
    err.classList.remove('hidden');
  }
  function clearDecodeMessages() {
    document.getElementById('decodeResult').classList.add('hidden');
    document.getElementById('decodeError').classList.add('hidden');
  }

  // Copy and save decoded message buttons
  document.getElementById('copyMessageBtn').addEventListener('click', () => {
      const text = document.getElementById('decodedMessage').value;
      navigator.clipboard.writeText(text).then(() => alert('Message copied to clipboard!'));
  });
  document.getElementById('saveMessageBtn').addEventListener('click', () => {
      const text = document.getElementById('decodedMessage').value;
      const blob = new Blob([text], {type:'text/plain'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'decoded_message.txt';
      a.click();
      URL.revokeObjectURL(url);
  });

  // File management
  const fileListDiv = document.getElementById('fileList');
  document.getElementById('refreshFileListBtn').addEventListener('click', refreshFileList);
  document.getElementById('openFilesFolderBtn').addEventListener('click', () => window.open('/web_outputs/', '_blank'));
  document.getElementById('openFolderBtn').addEventListener('click', () => window.open('/web_outputs/', '_blank'));

  async function refreshFileList() {
    try {
      const res = await fetch('/api/files');
      const files = await res.json();
      if (!files.length) {
        fileListDiv.innerHTML = '<p>No files found yet. Encode some messages to see them here!</p>';
        return;
      }
      fileListDiv.innerHTML = '';
      files.forEach(file => {
        const div = document.createElement('div');
        div.className = 'file-info';
        div.innerHTML = `<span>${file.name} (${file.size})</span>
          <div>
            <a href="/download/${file.name}" download class="btn-download" aria-label="Download ${file.name}">
              <i class="fas fa-download"></i>
            </a>
            <button class="btn-download" aria-label="Delete ${file.name}">🗑️</button>
          </div>
        `;
        div.querySelector('button').addEventListener('click', () => {
          if (confirm('Delete ' + file.name + '?')) deleteFile(file.name);
        });
        fileListDiv.appendChild(div);
      });
    } catch {
      fileListDiv.innerHTML = '<p>Error loading files.</p>';
    }
  }
  async function deleteFile(filename) {
    try {
      const res = await fetch('/api/delete/' + filename, { method: 'DELETE' });
      if(res.ok) refreshFileList();
      else alert('Failed to delete file');
    } catch(err) {
      alert('Error deleting file: ' + err.message);
    }
  }

  activateTab('encode');
  refreshFileList();

})();
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
        filename = request.form.get('filename', 'secure_image').strip()
        if not filename.lower().endswith('.png'):
            filename += '.png'

        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        filename = filename.replace(' ', '_') + '.png'
        output_path = os.path.join(OUTPUT_DIR, filename)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as input_tmp:
            image_file.save(input_tmp.name)
            input_path = input_tmp.name

        result = encode_data_into_image(
            input_path, message.encode(), password, output_path,
            lsb_bits=2, use_compression=True
        )
        os.unlink(input_path)

        if result['success']:
            encrypted_size = os.path.getsize(output_path)
            return jsonify({
                'success': True,
                'filename': filename,
                'message': result.get('message', ''),
                'security_score': result.get('security_score', 0),
                'encrypted_size': encrypted_size,
                'file_path': output_path,
            })
        else:
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

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image_file.save(tmp.name)
            input_path = tmp.name

        result = decode_data_from_image(input_path, password, 2)
        os.unlink(input_path)

        if result['success']:
            return jsonify({'success': True, 'message': result['data'].decode('utf-8')})
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
                fp = os.path.join(OUTPUT_DIR, filename)
                size = os.path.getsize(fp)
                files.append({'name': filename, 'size': f"{size/1024:.1f} KB"})
        return jsonify(files)
    except Exception:
        return jsonify([])

@app.route('/download/<filename>')
def download_file(filename):
    try:
        fp = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(fp):
            return send_file(fp, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        fp = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(fp):
            os.remove(fp)
            return '', 204
        return 'File not found', 404
    except Exception as e:
        return str(e), 500

@app.route('/web_outputs/')
def serve_outputs_directory():
    files = ""
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if filename.endswith('.png'):
            fp = os.path.join(OUTPUT_DIR, filename)
            size = os.path.getsize(fp)
            files += f'<li><a href="/download/{filename}" download>{filename}</a> ({size/1024:.1f} KB)</li>'
    return f"<html><body><h1>Web Outputs</h1><ul>{files}</ul><p><a href='/'>Back</a></p></body></html>"

if __name__ == '__main__':
    print("Starting StegSecure Pro...")
    print("Output dir:", OUTPUT_DIR)
    app.run(debug=True, host='0.0.0.0', port=5000)
