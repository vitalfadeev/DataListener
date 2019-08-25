import os
from flask import Flask, flash, request, redirect, url_for, render_template, Response, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, validators
from flask_basicauth import BasicAuth
from datalistener import settings
from datalistener import DataReadFromSql, DataStoreInSql, GetFileData
from datalistener import FORMAT_CSV, FORMAT_XLS, FORMAT_JSON, FORMAT_XML, DMY, MDY


# inti Flask
app = Flask(__name__)

# configure auth
app.config['BASIC_AUTH_USERNAME'] = settings.USERNAME
app.config['BASIC_AUTH_PASSWORD'] = settings.PASSWORD
basic_auth = BasicAuth(app)

# configure flask for file upload
app.config['SECRET_KEY'] = 'I have a dream'                 # secret key
app.config['UPLOADED_FILES_DEST'] = settings.UPLOAD_FOLDER  # fullpath to folder for store uploaded files

# configure file uploader
files = UploadSet('files', settings.ALLOWED_EXTENSIONS)     # setup file uploader
configure_uploads(app, files)                               # configure Flask app for file upload handling
patch_request_class(app, size=64 * 1024 * 1024)             # set maximum file size to 64MB, default is 16MB.


#####################################################################################################################
# Views
#####################################################################################################################
@app.route('/store', methods=['GET', 'POST', 'PUT'])
@basic_auth.required
def store():
    """ Store data into DB
        HTTP params:
            'file'      b""   supported formats: csv, xls, xlsx, json, xml
        :return: ""  Last id
    """
    # save file from HTTP data to local storage
    file = request.files['file']    # get file data
    filename = files.save(file)     # save file data

    # get full file name. ex: /full/path/to/file
    ffname = os.path.join(settings.UPLOAD_FOLDER, filename)

    # parse file & insert into DB. get last inserted ID
    lastid = ProcessFile( ffname )

    # return last inserted ID
    return Response(repr(lastid))


@app.route('/read', methods=['GET'])
@basic_auth.required
def read():
    """ Read data from DB
        HTTP params:
            'from_id'   0     Start ID.
            'format'    csv   Ouyput format: csv | xls | json | xml
        :return: file
    """
    from_id = request.args.get("from_id", None)
    format  = request.args.get("format", FORMAT_CSV)

    # read data from DB to [[],[],]
    data = ProcessRead(ExportLinesAfterPrimaryKey=from_id, FormatOutput=format)
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


#####################################################################################################################
# Store helper
#####################################################################################################################
def ProcessFile(ffname, SettingFormatDate=DMY):
    """ Read uploaded file, parse, insert into DB. Ir wrapper around main importer function.
        :param ffname:
        :return:
    """
    # read file (csv, xls, json, xml). into pandas.DataFrame
    df = GetFileData(ffname)

    # get column names common.
    # 1. get table columns
    # 2. get file columns
    # 3. find same
    dbcols = list(settings.ColumnType.keys())
    dfcols = list(df.columns)
    SameColumns = GetSameColumns(dbcols, dfcols)

    if SameColumns:
        # reduce data size: keep only required columns
        DataArrayToWrite = df[SameColumns]

        # remove NaN from data
        DataArrayToWrite = DataArrayToWrite.dropna()

        # insert into DB
        DatabaseName     = settings.BrainID
        TableName        = settings.TABLENAME
        ColumNames       = SameColumns

        # main function for store data to DB
        lastid = DataStoreInSql(DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY)

        return lastid

    else:
        # warning if no same columns
        warning = "Not all columns inserted. Expected: {}, Inserted: {}".format(dbcols, SameColumns)
        abort(500, warning)


#####################################################################################################################
# Read helper
#####################################################################################################################
def ProcessRead(ExportLinesAfterPrimaryKey=None, FormatOutput=FORMAT_CSV, SettingFormatDate=DMY):
    """ Wrapper around main exporter function
        :param ExportLinesAfterPrimaryKey:
        :param FormatOutput:
        :param SettingFormatDate:
        :return:
    """
    DatabaseName      = settings.BrainID
    TableName         = settings.TABLENAME

    # main function for read from DB & return to user as file
    DataArrayExported = DataReadFromSql( DatabaseName, TableName, ExportLinesAfterPrimaryKey, FormatOutput )

    return DataArrayExported


def GetSameColumns(db_cols, file_cols):
    """ Return names from first list if matched in second list
        :param db_cols:     [""]
        :param file_cols:   [""]
        :return:            [""] Same columns. ex: [a b c] & [a b d] = [a b]
    """
    common = set(db_cols) & set(file_cols)
    return list(common)

