import os
import uuid
import time
import subprocess
import threading
from datetime import datetime, timedelta
import sys
import webbrowser
from flask import Flask, render_template, request, send_from_directory, jsonify, abort

# Determine if running as a script or frozen exe
if getattr(sys, 'frozen', False):
    # If frozen, use the temporary folder for templates
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max upload limit
CLEANUP_AGE_MINUTES = 30

# Ensure directories exist (in the same dir as the exe)
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(base_dir, 'uploads')
OUTPUT_FOLDER = os.path.join(base_dir, 'output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_files():
    """Removes files older than CLEANUP_AGE_MINUTES from uploads and output."""
    now = time.time()
    cutoff = now - (CLEANUP_AGE_MINUTES * 60)
    
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder): continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    file_creation_time = os.path.getctime(file_path)
                    if file_creation_time < cutoff:
                        os.remove(file_path)
                        print(f"Cleaned up: {filename}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def get_file_size_mb(path):
    if os.path.exists(path):
        return os.path.getsize(path) / (1024 * 1024)
    return 0

def get_ffmpeg_path():
    """Finds the ffmpeg executable."""
    # Check if ffmpeg is in PATH
    from shutil import which
    if which("ffmpeg"):
        return "ffmpeg"
    
    # Check known Winget path (adjust user specific path if needed)
    known_path = r"C:\Users\ricar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
    if os.path.exists(known_path):
        return known_path

    # Check local folder (dist folder logic) - allows shipping ffmpeg with exe if needed
    local_ffmpeg = os.path.join(base_dir, 'ffmpeg.exe') 
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
        
    return "ffmpeg" 

def compress_video(input_path, output_path):
    """
    Compresses video using FFmpeg for WhatsApp compatibility.
    Goal: < 64MB, libx264, AAC 96k, CRF 28, 720p max.
    """
    ffmpeg_exe = get_ffmpeg_path()
    print(f"Using FFmpeg path: {ffmpeg_exe}") 

    command = [
        ffmpeg_exe,
        '-y',                 # Overwrite output file
        '-i', input_path,     # Input file
        '-c:v', 'libx264',    # Video codec
        '-preset', 'slow',    # Compression preset (slower = better compression/quality ratio)
        '-crf', '28',         # Constant Rate Factor (higher = more compression)
        '-vf', 'scale=\'min(1280,iw)\':-2', # Scale to max 1280px width, keep aspect ratio
        '-c:a', 'aac',        # Audio codec
        '-b:a', '96k',        # Audio bitrate
        '-movflags', '+faststart', # Optimize for web playback
        output_path
    ]
    
    try:
        # Prevent console window from popping up for FFmpeg on Windows if running from exe
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Run cleanup before processing new upload
    threading.Thread(target=cleanup_files).start()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Validate MIME type (basic check)
        if file.mimetype != 'video/mp4':
             return jsonify({'error': 'Invalid file type. Only MP4 is allowed.'}), 400

        # Generate unique filename
        filename = str(uuid.uuid4()) + ".mp4"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = f"compressed_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        try:
            file.save(input_path)
            
            original_size = get_file_size_mb(input_path)
            
            # Compress
            success = compress_video(input_path, output_path)
            
            if success:
                compressed_size = get_file_size_mb(output_path)
                reduction = 0
                if original_size > 0:
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                return jsonify({
                    'message': 'Compression successful',
                    'download_url': f'/download/{output_filename}',
                    'original_size': f"{original_size:.2f} MB",
                    'compressed_size': f"{compressed_size:.2f} MB",
                    'reduction': f"{reduction:.1f}%"
                })
            else:
                return jsonify({'error': 'Compression failed'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Auto-open browser
    port = 5000
    url = f"http://localhost:{port}"
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    app.run(debug=False, port=port)
