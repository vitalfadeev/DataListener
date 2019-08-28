import os
from flask import Flask, flash, request, redirect, url_for, render_template, Response, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_basicauth import BasicAuth
from datalistener import settings
from datalistener import DataReadFromSql, DataStoreInSql, GetFileData, get_db_connection
from datalistener import FORMAT_CSV, FORMAT_XLS, FORMAT_XLSX, FORMAT_JSON, FORMAT_XML, DMY, MDY


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
@app.route('/store', methods=['GET', 'POST'])
@basic_auth.required
def store():
    """ Store data into DB
        HTTP params:
            'file'      b""   supported formats: csv, xls, xlsx, json, xml
            or ?col1=value1&col2=value2 for HTTP GET/POST usage without file uploading
        :return: ""  Last id
    """
    lastid = None

    # detect format
    if request.files.get('file', None):
        # File sended
        format = 'FILE'

        # save file from HTTP data to local storage
        file = request.files['file']    # get file data
        filename = files.save(file)     # save file data

        # get full file name. ex: /full/path/to/file
        ffname = os.path.join(settings.UPLOAD_FOLDER, filename)

        # parse file & insert into DB. get last inserted ID
        lastid = ProcessFile( ffname )


    elif request.method == 'GET' and len(request.args) > 0:
        # HTTP GET | PUT sended
        format = 'HTTP-GET'

        # Check columns
        dbcols = settings.ColumnsNameInput + settings.ColumnsNameOutput
        dfcols = list(request.args)
        SameColumns = GetSameColumns(dbcols, dfcols)

        # if has same columns - OK
        if SameColumns:
            import pandas
            # insert into DB
            DatabaseName     = settings.BrainID                                         # DB name
            TableName        = settings.TABLENAME                                       # DB table name
            ColumNames       = SameColumns                                              # column names
            data             = [v for c,v in request.args.items() if c in SameColumns ] # one row
            DataArrayToWrite = [data]                                                   # table of one row

            # main function for store data to DB
            lastid = DataStoreInSql(DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY)

            # post insert service script
            PostInsert(1, lastid)

        else:
            # No same columns - [ warning ]
            abort(400, "No same columns")


    elif request.method == 'POST' and len(request.values) > 0:
        # HTTP POST sended
        format = 'HTTP-POST'
        # Check columns
        dbcols = settings.ColumnsNameInput + settings.ColumnsNameOutput
        dfcols = list(request.values)
        SameColumns = GetSameColumns(dbcols, dfcols)

        # if has same columns - OK
        if SameColumns:
            import pandas
            # insert into DB
            DatabaseName     = settings.BrainID                                           # DB name
            TableName        = settings.TABLENAME                                         # DB table name
            ColumNames       = SameColumns                                                # column names
            data             = [v for c,v in request.values.items() if c in SameColumns ] # one row
            DataArrayToWrite = [data]                                                     # table of one row

            # main function for store data to DB
            lastid = DataStoreInSql(DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY)

            # post insert service script
            PostInsert(1, lastid)

        else:
            # No same columns - [ warning ]
            abort(400, "No same columns")

    else:
        # unsupported HTTP method
        abort(400, "upsupported http method. expect GET or POST")

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

    elif format == FORMAT_XLSX:
        return Response(
            data,
            mimetype="application/xlsx",
            headers={"Content-disposition":"attachment; filename={}.xlsx".format(settings.TABLENAME)})

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
    dbcols = settings.ColumnsNameInput + settings.ColumnsNameOutput
    dfcols = list(df.columns)
    SameColumns = GetSameColumns(dbcols, dfcols)

    if SameColumns:
        # reduce data size: keep only required columns
        DataArrayToWrite = df[SameColumns]

        # insert into DB
        DatabaseName     = settings.BrainID
        TableName        = settings.TABLENAME
        ColumNames       = SameColumns

        # main function for store data to DB
        lastid = DataStoreInSql(DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY)

        # post insert service script
        PostInsert(df.shape[0], lastid)

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


def PostInsert(rows_count, lastid):
    """ Post Insert service script.
        Update predefined columns: 'IsForLearning' and other
        :param rows_count int  Row in data packet
        :param lastid     int  Last inserted ID
    """
    DatabaseName = settings.BrainID             # DB name
    TableName    = settings.TABLENAME           # DB table name
    cols_in      = settings.ColumnsNameInput    # input columns
    cols_out     = settings.ColumnsNameOutput   # output columns

    # get DB connection
    dbc = get_db_connection(DatabaseName)

    # After all lines stored, it is possible to execute a sql command to update IsForLearning=1 for all lines with no values empty in all (columnsInput+columnsOutPut)
    # make SQL condition: LENGTH(Col1) > 0 AND Col1 IS NOT NULL ...
    conds = []
    for col in cols_in + cols_out:
        conds.append( "LENGTH(`{}`) > 0 AND `{}` IS NOT NULL".format(col, col) )
    cond = " AND ".join( conds )

    # execute sql
    dbc.execute("""
        UPDATE `{}` 
           SET IsForLearning = 1 
         WHERE {}"""
        .format(
            TableName,
            cond
        )
    )

    # After all lines stored, it is possible to execute a sql command to update IsForSolving=1 for all lines with all values in (columnsInput) and none or some values in columnsOutPut
    # make SQL condition: LENGTH(Col1) > 0 AND Col1 IS NOT NULL ...
    conds = []
    for col in cols_in:
        conds.append( "LENGTH(`{}`) > 0 AND `{}` IS NOT NULL".format(col, col) )
    cond = " AND ".join( conds )

    # execute sql
    dbc.execute("""
        UPDATE `{}` 
           SET IsForSolving = 1 
         WHERE {}"""
        .format(
            TableName,
            cond
        )
    )

    # After all lines stored, it is possible to execute a sql command to update IsWithMissingValues=1 for all lines with some values missing in columnsInput
    conds = []
    for col in cols_in:
        conds.append( "( LENGTH(`{}`) = 0 OR `{}` IS NULL )".format(col, col) )
    cond = " AND ".join( conds )

    # execute sql
    dbc.execute("""
        UPDATE `{}` 
           SET IsWithMissingValues = 1 
         WHERE {}"""
        .format(
            TableName,
            cond
        )
    )


    # After all lines stored, it is possible to execute a sql command to update IsForEvluation=1  on 10% lines (Max 100 lines) where  IsForLearning=1
    conds = []
    # get chunk id
    chunk_size = int(rows_count / 10)  # 10%
    if chunk_size > 100:
        chunk_size = 100

    chunk_id = lastid - chunk_size
    if chunk_id < 0:
        chunk_id = 0

    # execute sql
    dbc.execute("""
        UPDATE `{}` 
           SET IsForEvaluation = 1 
         WHERE IsForLearning = 1 AND ID > {}"""
        .format(
            TableName,
            chunk_id
        )
    )



if 0:
    import os
    from flask import Flask, flash, request, redirect, url_for, render_template, Response, abort
    from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField, FileRequired, FileAllowed
    from wtforms import SubmitField, StringField, validators


    ###################################### devel forms ######################################
    # dev test function
    @app.route("/")
    def hello():
        return "Data listener ready!"


    # upload form
    class UploadForm(FlaskForm):
        file = FileField(validators=[FileAllowed(files, ", ".join(settings.ALLOWED_EXTENSIONS) + ' only'), FileRequired(u'File was empty!')])
        submit = SubmitField('Upload')


    # upload form
    class ReadForm(FlaskForm):
        databasename = StringField('DatabaseName', [validators.required(), validators.length(max=20)], default=settings.BrainID)
        tablename    = StringField('TableName', [validators.required(), validators.length(max=20)], default=settings.TABLENAME)
        exportlines  = StringField('ExportLines', [validators.required(), validators.length(max=20)], default="5")
        formatoutput = StringField('FormatOutput', [validators.required(), validators.length(max=20)], default="csv")
        submit = SubmitField('Read')


    @app.route('/store-dev', methods=['GET', 'POST', 'PUT'])
    @basic_auth.required
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
            lastid = ProcessFile( ffname )


        else:
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
            )


    @app.route('/read-dev', methods=['GET', 'POST'])
    @basic_auth.required
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


