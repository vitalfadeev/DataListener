import os
from functools import wraps
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from dattalistener import settings
import pandas as pd



ALLOWED_EXTENSIONS = {'json', 'csv', 'xls', 'xlsx', 'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER


def login_required(func):
    """ Decorator for check user/password
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ?username=test&password=test
        username = request.args.get('username', None)
        password = request.args.get('password', None)

        if username == settings.USERNAME and password == settings.PASSWORD:
            return func(*args, **kwargs)
        else:
            return "Access denied"

    return wrapper


@app.route("/")
def hello():
    return "Data listener ready!"


@app.route('/store', methods=['GET'])
@login_required
def store_get():
    # request.args
    return "secret!"


@app.route('/store', methods=['POST'])
@login_required
def store_post():
    # request.form
    # request.data
    # request.files
    # request.values
    # request.json

    request.files

    return "secret!"


def read_csv():
    pd.read_csv()


def extract_columns():
    pass



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file():
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

    #
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))

    return ""
