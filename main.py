import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask import send_file

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'xml'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


SEDIT_PATH = 'C:\Program Files\Subtitle Edit\SubtitleEdit.exe'


@app.route('/')
def hello():
    return 'hello'


@app.route('/convert-srt', methods=['POST'])
def convert_srt():
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        subprocess.Popen(
            [SEDIT_PATH, "/convert", file_path, "srt", "/fixcommonerrors", "/encoding:utf-8",
             "/RemoveLineBreaks", "/MergeSameTimeCodes", "/MergeShortLines", "/FixCommonErrors"], shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        return send_file(file_path.replace('xml', 'srt'), mimetype='application/x-subrip')
    else:
        resp = jsonify({'message': 'Allowed file types are xml'})
        resp.status_code = 400
        return resp


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.dirname(__file__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.run(host="0.0.0.0", port=8080, threaded=True)
