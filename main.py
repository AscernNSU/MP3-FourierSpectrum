
import os

from flask import Flask, escape, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
#from librosa.core import stft


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_ext = os.path.abspath(app.config['UPLOAD_FOLDER'] + filename)
            #file.save(file.filename)
            file.save(filename_ext)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder_abspath = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder_abspath,
                               filename)


#if __name__ == '__main__':
#    app.run()
