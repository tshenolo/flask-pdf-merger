import os
from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/app/uploaded_pdfs'  # Absolute path in Docker
app.secret_key = "your_secret_key"

from app import routes
