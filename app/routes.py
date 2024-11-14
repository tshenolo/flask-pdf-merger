from flask import render_template, request, redirect, url_for, flash, session, send_file
import os
import uuid
from PyPDF2 import PdfMerger
from app import app

@app.route('/')
def upload():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("files[]")
    
    # Generate a unique directory for the session
    session_id = str(uuid.uuid4())
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(upload_folder, exist_ok=True)
    session['upload_folder'] = upload_folder  # Store folder path in session

    file_paths = []
    for file in uploaded_files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_paths.append(file.filename)

    return redirect(url_for('select_files', files=file_paths))

@app.route('/select_files')
def select_files():
    files = request.args.getlist('files')
    return render_template('select.html', files=files)

@app.route('/combine', methods=['POST'])
def combine():
    upload_folder = session.get('upload_folder')
    if not upload_folder:
        flash("Session expired or invalid folder.")
        return redirect(url_for('upload'))
    
    selected_files = request.form.getlist('files')
    ordered_files = request.form.getlist('ordered_files')

    merger = PdfMerger()
    for filename in ordered_files:
        filepath = os.path.join(upload_folder, filename)
        merger.append(filepath)

    output_filename = 'combined.pdf'
    output_path = os.path.join(upload_folder, output_filename)
    merger.write(output_path)
    merger.close()

    # Verify if the file was created successfully
    if not os.path.exists(output_path):
        flash("Failed to create the combined PDF file.")
        return redirect(url_for('upload'))

    # Extract the folder name (session_id) from the upload folder path
    session_id = os.path.basename(upload_folder)

    # Redirect to result page with a download link
    return redirect(url_for('result', filename=output_filename, folder=session_id))



@app.route('/result')
def result():
    filename = request.args.get('filename')
    folder = request.args.get('folder')
    download_url = url_for('download_file', folder=folder, filename=filename)
    return render_template('result.html', download_url=download_url)

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
    return send_file(file_path, as_attachment=True)
