import os
from functools import wraps
from flask import Flask, flash, request, redirect, url_for, render_template, Response, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, validators
from datalistener import settings
#from datalistener.backend.pandas import DataReadFromSql, DataStoreInSql, GetFileData
#from datalistener.backend.formats import FORMAT_CSV, FORMAT_XLS, FORMAT_JSON, FORMAT_XML, DMY, MDY

from datalistener import DataReadFromSql, DataStoreInSql, GetFileData
from datalistener import FORMAT_CSV, FORMAT_XLS, FORMAT_JSON, FORMAT_XML, DMY, MDY


# inti Flask
app = Flask(__name__)

# configure flask
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_FILES_DEST'] = settings.UPLOAD_FOLDER

# configure flask uploader
files = UploadSet('files', settings.ALLOWED_EXTENSIONS)
configure_uploads(app, files)
patch_request_class(app)  # set maximum file size, default is 16MB


# decorator for check login/password
def login_required(func):
    """ Decorator for check user/password
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ?username=test&password=test
        if request.method in ['POST', 'PUT']:
            username = request.values.get('username', None)
            password = request.values.get('password', None)
        else:
            username = request.args.get('username', None)
            password = request.args.get('password', None)

        # check username & password
        if username == settings.USERNAME and password == settings.PASSWORD:
            return func(*args, **kwargs) # OK
        else:
            abort(403) # access denied

    return wrapper


@app.route('/store', methods=['GET', 'POST', 'PUT'])
@login_required
def store():
    """ Store data into DB
        HTTP params:
            'username'  ""
            'password'  ""
            'file'      b""
        :return: ""  Last id
    """
    # save file from HTTP data to local storage
    file = request.files['file']
    filename = files.save(file)

    # get full file name. ex: /full/path/to/file
    ffname = os.path.join(settings.UPLOAD_FOLDER, filename)

    # parse file & insert into DB
    (lastid, head, tail, dbcols, dfcols, matches) = ProcessFile( ffname )

    if len(matches) != len(dbcols):
        warning = "Not all columns inserted. Expected: {}, Inserted: {}".format(dbcols, matches)
        return warning
    else:
        return Response(repr(lastid))


@app.route('/read', methods=['GET'])
@login_required
def read():
    """ Read data from DB
        HTTP params:
            'username'  ""
            'password'  ""
            'id'        0    Start ID.
            'format'    csv   Ouyput format: csv | xls | json | xml
        :return: file
    """
    id_ = request.args.get("id", None)
    format = request.args.get("format", FORMAT_CSV)

    data = ProcessRead(ExportLinesAfterPrimaryKey=id_, FormatOutput=format)
    if format == FORMAT_CSV:
        return Response(
            data,
            mimetype="text/csv",
            headers={"Content-disposition":"attachment; filename={}.csv".format(settings.TABLENAME)})

    elif format == FORMAT_XLS:
        return Response(
            data,
            mimetype="application/xls",
            headers={"Content-disposition":"attachment; filename={}.xls".format(settings.TABLENAME)})

    elif format == FORMAT_JSON:
        return Response(
            data,
            mimetype="application/json",
            headers={"Content-disposition":"attachment; filename={}.json".format(settings.TABLENAME)})

    elif format == FORMAT_XML:
        return Response(
            data,
            mimetype="application/xml",
            headers={"Content-disposition":"attachment; filename={}.xml".format(settings.TABLENAME)})

    else:
        raise Exception("unsupported")


###################################### devel forms ######################################
# dev test function
@app.route("/")
def hello():
    return "Data listener ready!"


# upload form
class UploadForm(FlaskForm):
    username = StringField('Username', [validators.required(), validators.length(max=20)])
    password = StringField('Password', [validators.required(), validators.length(max=20)])
    file = FileField(validators=[FileAllowed(files, ", ".join(settings.ALLOWED_EXTENSIONS) + ' only'), FileRequired(u'File was empty!')])
    submit = SubmitField('Upload')


# upload form
class ReadForm(FlaskForm):
    username     = StringField('Username', [validators.required(), validators.length(max=20)])
    password     = StringField('Password', [validators.required(), validators.length(max=20)])
    databasename = StringField('DatabaseName', [validators.required(), validators.length(max=20)], default=settings.BrainID)
    tablename    = StringField('TableName', [validators.required(), validators.length(max=20)], default=settings.TABLENAME)
    exportlines  = StringField('ExportLines', [validators.required(), validators.length(max=20)], default="5")
    formatoutput = StringField('FormatOutput', [validators.required(), validators.length(max=20)], default="csv")
    submit = SubmitField('Read')


@app.route('/store-dev', methods=['GET', 'POST', 'PUT'])
@login_required
def store_dev():
    """ Store data into DB
        :return: ""  Last row id
    """
    form = UploadForm()
    if form.validate_on_submit():
        # save file from HTTP data to local storage
        filename = files.save(form.file.data)
        file_url = files.url(filename)

        # get full file name. ex: /full/path/to/file
        ffname = os.path.join(settings.UPLOAD_FOLDER, filename)

        # parse file & insert into DB
        (lastid, head, tail, dbcols, dfcols, matches) = ProcessFile( ffname )

        if len(matches) != len(dbcols):
            warning = "Not all columns inserted. Expected: {}, Inserted: {}".format(dbcols, matches)
        else:
            warning = None

    else:
        form.username.default = request.args.get('username', '')
        form.password.default = request.args.get('password', '')
        form.process()
        file_url = None
        lastid = None
        head = None
        tail = None
        dbcols = None
        dfcols = None
        matches = None
        warning = None

    return render_template('store.html',
        form=form,
        file_url=file_url,
        LastPrimaryKeyWritten=lastid,
        head=head,
        tail=tail,
        dbcols=dbcols,
        dfcols=dfcols,
        matches=matches,
        warning=warning
        )


@app.route('/read-dev', methods=['GET', 'POST'])
@login_required
def read_dev():
    """ Read data from DB
        :return: []
    """
    form = ReadForm()
    if form.validate_on_submit():
        warning = None
        data = ProcessRead()
        return Response(
            data,
            mimetype="text/csv",
            headers={"Content-disposition":"attachment; filename={}.csv".format(settings.TABLENAME)})
    else:
        warning = None
        data = ""

    return render_template('read.html',
        form=form,
        warning=warning,
        data=data
        )


#######################################################################################
def ProcessFile(ffname, SettingFormatDate=DMY):
    """ Read uploaded file, parse, insert into DB
        :param ffname:
        :return:
    """
    # read file (csv, xls, json, xml)
    df = GetFileData(ffname)

    # get column names common in file and in table
    dbcols = list(settings.ColumnType.keys())
    dfcols = list(df.columns)
    RequiredColumns = GetCommonColumns(dbcols, dfcols)

    if RequiredColumns:
        # reduce data size: keep only required columns
        RequiredData = df[RequiredColumns]

        # remove NaN from data
        RequiredData = RequiredData.dropna()

        # insert into DB
        DatabaseName     = settings.BrainID
        TableName        = settings.TABLENAME
        ColumNames       = RequiredColumns
        DataArrayToWrite = RequiredData.values.tolist()

        lastid = DataStoreInSql(DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY)

        # head
        head = RequiredData.head()
        tail = RequiredData.tail()

        return (lastid, head, tail, dbcols, dfcols, ColumNames)

    else:
        abort(500, "No common columns")


def ProcessRead(ExportLinesAfterPrimaryKey=None, FormatOutput=FORMAT_CSV, SettingFormatDate=DMY):
    DatabaseName      = settings.BrainID
    TableName         = settings.TABLENAME

    DataArrayExported = DataReadFromSql( DatabaseName, TableName, ExportLinesAfterPrimaryKey, FormatOutput )

    return DataArrayExported


def GetCommonColumns(db_cols, file_cols):
    common = set(db_cols) & set(file_cols)
    return list(common)

