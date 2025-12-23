import os
import mammoth
from flask import Flask, render_template, send_from_directory, abort, request

app = Flask(__name__)

# Configuration
# UPDATE THIS PATH to point to your actual data directory
# Example: CONTENT_ROOT = '/home/user/my_documents'
CONTENT_ROOT = '/Users/nishantmohil/Documents/DPP'

@app.route('/')
def index():
    return browse('')

@app.route('/browse/')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):
    """
    List contents of the directory.
    Safe path handling by resolving absolute paths.
    """
    # Securely resolve the path
    abs_path = os.path.normpath(os.path.join(CONTENT_ROOT, subpath))
    
    # Ensure the path is within CONTENT_ROOT (prevent traversal)
    if not abs_path.startswith(CONTENT_ROOT):
        abort(403)
        
    if not os.path.exists(abs_path):
        abort(404)
        
    if os.path.isfile(abs_path):
        # If user browses to a file directly, redirect to view
        # logic or handle as download. For now, let's assume browse is for dirs.
        return "Not a directory", 400

    items = []
    try:
        # List directory contents
        for name in os.listdir(abs_path):
            if name.startswith('.'): continue # Skip hidden files
            
            full_path = os.path.join(abs_path, name)
            is_dir = os.path.isdir(full_path)
            
            rel_path = os.path.relpath(full_path, CONTENT_ROOT)
            
            items.append({
                'name': name,
                'is_dir': is_dir,
                'path': rel_path
            })
            
        # Sort directories first, then files
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
    except OSError as e:
        return str(e), 500

    # Breadcrumbs
    breadcrumbs = []
    parts = subpath.strip('/').split('/')
    if parts == ['']: parts = []
    
    current_path = ''
    for part in parts:
        current_path = os.path.join(current_path, part)
        breadcrumbs.append({'name': part, 'path': current_path})

    return render_template('index.html', items=items, current_path=subpath, breadcrumbs=breadcrumbs)

@app.route('/view/<path:filepath>')
def view_file(filepath):
    abs_path = os.path.normpath(os.path.join(CONTENT_ROOT, filepath))
    
    if not abs_path.startswith(CONTENT_ROOT):
        abort(403)
    if not os.path.exists(abs_path):
        abort(404)
        
    filename = os.path.basename(abs_path)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.docx':
        # Use client-side rendering for better fidelity (math, complex layouts)
        return render_template('view_docx.html', filename=filename, file_url=f'/download/{filepath}')
            
    elif ext == '.pdf':
        # Serve the PDF file for the browser's native viewer or embed it
        # We can pass the URL to the download route which serves the raw file
        return render_template('view_pdf.html', filename=filename, file_url=f'/download/{filepath}')
        
    else:
        # Fallback for other files
        return f"Cannot view this file type. <a href='/download/{filepath}'>Download</a>"

@app.route('/download/<path:filepath>')
def download_file(filepath):
    abs_path = os.path.normpath(os.path.join(CONTENT_ROOT, filepath))
    if not abs_path.startswith(CONTENT_ROOT):
        abort(403)
    return send_from_directory(CONTENT_ROOT, filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
