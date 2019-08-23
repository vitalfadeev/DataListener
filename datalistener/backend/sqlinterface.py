import os
from datalistener import settings
from sqlinterface import SQLInterface
from .formats import FORMAT_CSV, FORMAT_XLS, FORMAT_JSON, FORMAT_XML, DMY, MDY


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_CNF_PATH = os.path.join(BASE_DIR, 'my.cnf')


def DataStoreInSql( DatabaseName, TableName, ColumNames, DataArrayToWrite ):
    """ Insert data into DB
        :param DatabaseName:     ""
        :param TableName:        ""
        :param ColumNames:       []
        :param DataArrayToWrite: [[],[],]
        :return:
    """
    # insert into DB
    from sqlinterface import SQLInterface

    # prepare database and table
    db = SQLInterface(my_cnf_path=MY_CNF_PATH)
    db.SqlDropDatabase(DatabaseName)
    db.SqlCreateDatabase(DatabaseName)
    db.UseDatabase(DatabaseName)
    db.SqlCreateTable(TableName, settings.TABLE_COLS)

    # insert
    c = db.SqlExecuteManyInsert(TableName, ColumNames, DataArrayToWrite)

    # last id
    LastPrimaryKeyWritten = c.lastrowid + c.rowcount - 1

    return LastPrimaryKeyWritten


def DataReadFromSql( DatabaseName, TableName, ExportLinesAfterPrimaryKey=None, FormatOutput=FORMAT_CSV ):
    """ Read from DB
    :param DatabaseName:                ""
    :param TableName:                   ""
    :param ExportLinesAfterPrimaryKey:  ""
    :param FormatOutput:                ""
    :return:                            b""
    """
    # prepare database and table
    db = SQLInterface()
    db.UseDatabase(DatabaseName)

    # read
    columns = None

    if ExportLinesAfterPrimaryKey:
        sql_where = " id >= {}".format( ExportLinesAfterPrimaryKey )
    else:
        sql_where = None

    datas = db.SqlExecuteManyRead( TableName, columns, sql_where )

    if FormatOutput == FORMAT_CSV:
        import csv
        import tempfile

        # create teno file
        fd, csv_file = tempfile.mkstemp(prefix="DataReadFromSql-", suffix=".csv")

        # write header & rows
        with open(csv_file, 'w', newline='\n') as f:
            writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # write header
            cursor = db.raw("SELECT * FROM `{}` LIMIT 1".format(TableName))
            table_cols = [ coldesc[0] for coldesc in cursor.description ] # get column names
            writer.writerow(table_cols)

            # write rows
            for row in datas:
                writer.writerow(row)

        # read content
        with open(csv_file, 'rb') as f:
            DataArrayExported = f.read()

        # close the file descriptor
        os.close(fd)

    else:
        raise Exception("unsupported")

    return DataArrayExported


def GetFileData( filename ):
    # read data
    return None
