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
        (lastid, head, tail, dbcols, dfcols, matches) = ProcessFile( ffname )

        if len(matches) != len(dbcols):
            warning = "Not all columns inserted. Expected: {}, Inserted: {}".format(dbcols, matches)
        else:
            warning = None

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
        head=head,
        tail=tail,
        dbcols=dbcols,
        dfcols=dfcols,
        matches=matches,
        warning=warning
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


