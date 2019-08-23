import os
import pandas
from .formats import FORMAT_CSV, FORMAT_XLS, FORMAT_JSON, FORMAT_XML, DMY, MDY


DRIVER = 'sqlite'


def DataStoreInSql( DatabaseName, TableName, ColumNames, DataArrayToWrite, SettingFormatDate=DMY ):
    """ Insert data into DB
        :param DatabaseName:     ""
        :param TableName:        ""
        :param ColumNames:       []
        :param DataArrayToWrite: [[],[],]
        :return:
    """
    # dataframe
    df = pandas.DataFrame(DataArrayToWrite, columns=ColumNames)

    # insert into DB
    connection = get_db_connection( DatabaseName )

    df.to_sql(TableName, connection, if_exists='replace', method='multi', index_label='ID')

    # last id
    result = connection.execute("SELECT max(id) FROM `{}`;".format(TableName))
    row = result.fetchone()
    LastPrimaryKeyWritten = row[0]

    connection.close()

    return LastPrimaryKeyWritten


def DataReadFromSql( DatabaseName, TableName, ExportLinesAfterPrimaryKey=None, FormatOutput=FORMAT_CSV ):
    """ Read from DB
    :param DatabaseName:                ""
    :param TableName:                   ""
    :param ExportLinesAfterPrimaryKey:  ""
    :param FormatOutput:                ""
    :return:                            b""
    """
    #
    connection = get_db_connection( DatabaseName )

    #
    sql = "SELECT * FROM `{}`".format(TableName)
    if ExportLinesAfterPrimaryKey:
        sql = sql + " WHERE id >= {}".format( ExportLinesAfterPrimaryKey )

    df = pandas.read_sql_query( sql, connection, index_col="ID" )

    if FormatOutput == FORMAT_CSV:
        DataArrayExported = df.to_csv(sep="\t" )

    elif FormatOutput == FORMAT_XLS:
        import tempfile

        fd, xls_file = tempfile.mkstemp(prefix="DataReadFromSql-", suffix=".xls")

        df.to_excel(xls_file)

        # use a context manager to open the file at that path and close it again
        with open(xls_file, 'rb') as f:
            DataArrayExported = f.read()

        # close the file descriptor
        os.close(fd)

        # remove temp file
        if os.path.isfile(xls_file):
            os.remove(xls_file)

    elif FormatOutput == FORMAT_JSON:
        DataArrayExported = df.to_json()

    elif FormatOutput == FORMAT_XML:
        DataArrayExported = df.to_xml()

    else:
        raise Exception("unsupported")

    return DataArrayExported


### helpers ###
def to_xml(df, filename=None, mode='w'):
    def row_to_xml(row):
        xml = ['<item>']
        for i, col_name in enumerate(row.index):
            xml.append('  <field name="{0}">{1}</field>'.format(col_name, row.iloc[i]))
        xml.append('</item>')
        return '\n'.join(xml)
    res = '\n'.join(df.apply(row_to_xml, axis=1))

    if filename is None:
        return res
    with open(filename, mode) as f:
        f.write(res)


pandas.DataFrame.to_xml = to_xml


def GetFileData( filename ):
    # read data
    if filename.endswith('csv'):
        df = GetFileDataCSV(filename)

    elif filename.endswith('xls'):
        df = GetFileDataXLS(filename)

    elif filename.endswith('xlsx'):
        df = GetFileDataXLS(filename)

    elif filename.endswith('json'):
        df = GetFileDataJSON(filename)

    elif filename.endswith('xml'):
        df = GetFileDataXML(filename)

    else:
        raise Exception("Unsuppported")

    return df


def GetFileDataCSV(filename):
    """ Read csv file with data
        :param filename:    "" file name
        :return:            pandas Dataframe
    """
    df = pandas.read_csv(filename, sep=None, engine='python')
    return df


def GetFileDataXLS(filename):
    df = pandas.read_excel(filename)
    return df


def GetFileDataJSON(filename):
    df = pandas.read_json(filename)
    return df


def GetFileDataXML(filename):
    df = pandas.read_html(filename)
    return df


def get_db_connection_mysql(DatabaseName):
    from sqlalchemy import create_engine
    from sqlalchemy.engine.url import URL

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(BASE_DIR)
    MY_CNF_PATH = os.path.join(BASE_DIR, 'my.cnf')

    myDB = URL(
        drivername='mysql',
        host='localhost',
        database=DatabaseName,
        query={'read_default_file': MY_CNF_PATH}
    )
    engine = create_engine(name_or_url=myDB)
    connection = engine.connect()

    return connection


def get_db_connection_sqlite(DatabaseName):
    from sqlalchemy import create_engine

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(BASE_DIR)
    BASE_DIR = os.path.dirname(BASE_DIR)
    abspath = os.path.abspath(os.path.join(BASE_DIR, DatabaseName + '.sqlite3'))

    engine = create_engine('sqlite:///{}'.format(abspath))
    connection = engine.connect()

    return connection


def get_db_connection(DatabaseName):
    if DRIVER == 'sqlite':
        return get_db_connection_sqlite(DatabaseName)
    else:
        return get_db_connection_mysql(DatabaseName)
