// Tab navigation
function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

// File upload handling
function setupFileUpload(uploadAreaId, fileInputId, previewId) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    const preview = document.getElementById(previewId);

    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#e3f2fd';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(fileInput, preview);
        }
    });
    
    fileInput.addEventListener('change', () => handleFileSelect(fileInput, preview));
}

function handleFileSelect(input, preview) {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            
            // Calculate capacity for encode tab
            if (input.id === 'encodeImage') {
                calculateCapacity(e.target.result);
            }
        };
        reader.readAsDataURL(file);
    }
}

// Capacity calculation
async function calculateCapacity(imageData) {
    const lsbBits = document.getElementById('lsbBits').value;
    
    try {
        const response = await fetch('/api/capacity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData, lsb_bits: lsbBits })
        });
        
        const data = await response.json();
        if (data.success) {
            document.getElementById('capacityInfo').textContent = 
                `Capacity: ${data.capacity.capacity_bytes} bytes (${data.capacity.capacity_kb} KB)`;
        }
    } catch (error) {
        console.error('Capacity calculation failed:', error);
    }
}

// Encode function
async function encodeImage() {
    const imageInput = document.getElementById('encodeImage');
    const message = document.getElementById('secretMessage').value;
    const password = document.getElementById('encodePassword').value;
    const lsbBits = document.getElementById('lsbBits').value;
    const useCompression = document.getElementById('useCompression').checked;
    
    if (!imageInput.files[0]) {
        alert('Please select an image first');
        return;
    }
    if (!message) {
        alert('Please enter a secret message');
        return;
    }
    if (!password) {
        alert('Please enter a password');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('message', message);
    formData.append('password', password);
    formData.append('lsb_bits', lsbBits);
    formData.append('compression', useCompression);
    
    try {
        document.body.classList.add('loading');
        const response = await fetch('/api/encode', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('encodeResult');
            const preview = document.getElementById('stegoPreview');
            const scoreDiv = document.getElementById('securityScore');
            
            preview.innerHTML = `<img src="${data.image}" alt="Stego Image">`;
            scoreDiv.textContent = `Security Score: ${(data.security_score * 100).toFixed(1)}%`;
            scoreDiv.className = `security-score ${
                data.security_score > 0.7 ? 'high' : 
                data.security_score > 0.4 ? 'medium' : 'low'
            }`;
            
            resultDiv.style.display = 'block';
        } else {
            alert('Encoding failed: ' + data.error);
        }
    } catch (error) {
        alert('Encoding error: ' + error.message);
    } finally {
        document.body.classList.remove('loading');
    }
}

// Decode function
async function decodeImage() {
    const imageInput = document.getElementById('decodeImage');
    const password = document.getElementById('decodePassword').value;
    const lsbBits = document.getElementById('decodeLsbBits').value;
    
    if (!imageInput.files[0]) {
        alert('Please select an image first');
        return;
    }
    if (!password) {
        alert('Please enter the password');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('password', password);
    formData.append('lsb_bits', lsbBits);
    
    try {
        document.body.classList.add('loading');
        const response = await fetch('/api/decode', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('decodeResult');
            const messageDiv = document.getElementById('decodedMessage');
            
            messageDiv.textContent = data.message;
            resultDiv.style.display = 'block';
        } else {
            alert('Decoding failed: ' + data.error);
        }
    } catch (error) {
        alert('Decoding error: ' + error.message);
    } finally {
        document.body.classList.remove('loading');
    }
}

// Analyze function
async function analyzeImage() {
    const imageInput = document.getElementById('analyzeImage');
    
    if (!imageInput.files[0]) {
        alert('Please select an image first');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    
    try {
        document.body.classList.add('loading');
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('analyzeResult');
            const reportDiv = document.getElementById('analysisReport');
            
            reportDiv.textContent = `Security Score: ${(data.security_score * 100).toFixed(1)}%
Security Level: ${data.security_level}
Detection Risk: ${data.detection_risk}

Recommendation:
${data.recommendation}`;
            
            resultDiv.style.display = 'block';
        } else {
            alert('Analysis failed: ' + data.error);
        }
    } catch (error) {
        alert('Analysis error: ' + error.message);
    } finally {
        document.body.classList.remove('loading');
    }
}

// Utility functions
function downloadStegoImage() {
    const img = document.querySelector('#stegoPreview img');
    if (img) {
        const link = document.createElement('a');
        link.href = img.src;
        link.download = 'stego_image.png';
        link.click();
    }
}

function saveDecodedMessage() {
    const message = document.getElementById('decodedMessage').textContent;
    const blob = new Blob([message], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'decoded_message.txt';
    link.click();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload('encodeUpload', 'encodeImage', 'encodePreview');
    setupFileUpload('decodeUpload', 'decodeImage', 'decodePreview');
    setupFileUpload('analyzeUpload', 'analyzeImage', 'analyzePreview');
    
    // Update capacity when LSB bits change
    document.getElementById('lsbBits').addEventListener('change', () => {
        const preview = document.querySelector('#encodePreview img');
        if (preview) {
            calculateCapacity(preview.src);
        }
    });
});