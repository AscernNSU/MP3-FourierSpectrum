import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, flash, redirect

from werkzeug.utils import secure_filename
from librosa import amplitude_to_db
from librosa.display import specshow
from librosa.core import load, stft

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'uploads/'
STATIC_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

matplotlib.use('Agg')


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
            file.save(filename_ext)
            half_sampling_rate = 22050
            stft_half_length = 1024
            upload_folder_abspath = os.path.abspath(app.config['UPLOAD_FOLDER'])
            upload_file_abspath = upload_folder_abspath + '\\' + filename
            os.chmod(upload_file_abspath, 0o777)

            file_data = load(upload_file_abspath, half_sampling_rate, True)
            np_data = np.array(file_data[0])
            plt.rcParams.update({'font.size': 12})
            freq = np.linspace(0, 2 * half_sampling_rate, stft_half_length)
            spec = stft(np_data, 2 * stft_half_length - 1)
            abs_spec = np.abs(spec)

            specshow(amplitude_to_db(abs_spec, ref=np.max), y_axis='log', x_axis='time')
            plt.title('Спектрограмма мощности')
            cbar = plt.colorbar(format='%+2.0f dB')
            plt.tight_layout()

            fig2d_path = os.path.abspath(APP_ROOT + "\\static\\spectrum-2D.png")
            plt.savefig(fig2d_path)
            cbar.remove()
            return render_template('mp3spec.html')

    elif request.method == 'GET':
        return '''
    <!doctype html>
    <title>Fourier spectrum visualization of audio mp3 File</title>
    <h1 align="center" style="font-family:verdana">Добро пожаловать на страницу визуализации cпектра аудиофайлов!
    Нажмите кнопку "Обзор...", чтобы загрузить аудиофайл. </h1>
    <div align="center">
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
    </div>
    '''


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run()
