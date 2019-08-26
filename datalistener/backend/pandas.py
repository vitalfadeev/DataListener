import os
import pandas
from .formats import *


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

    # get connection
    connection = get_db_connection( DatabaseName )

    # insert into DB. if table not exists - create, if exists - append
    df.to_sql(TableName, connection, if_exists='append', method='multi', index_label='ID', index=False)

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

    elif FormatOutput == FORMAT_XLSX:
        import tempfile

        fd, xlsx_file = tempfile.mkstemp(prefix="DataReadFromSql-", suffix=".xlsx")

        df.to_excel(xlsx_file)

        # use a context manager to open the file at that path and close it again
        with open(xlsx_file, 'rb') as f:
            DataArrayExported = f.read()

        # close the file descriptor
        os.close(fd)

        # remove temp file
        if os.path.isfile(xlsx_file):
            os.remove(xlsx_file)

    elif FormatOutput == FORMAT_JSON:
        DataArrayExported = df.to_json(orient='records')

    elif FormatOutput == FORMAT_XML:
        DataArrayExported = df.to_xml()

    else:
        raise Exception("unsupported")

    return DataArrayExported


### helpers ###
def to_xml(df, filename=None, mode='w'):
    """ Save DataFrame to XML. If file == None return string.
        :param df:
        :param filename:
        :param mode:
        :return: ""
        Note: XML format
            <table>
                <tr>
                    <Col1>...</Col1> <Col2>...</Col2>
                </tr>
            </table>
    """
    def row_to_xml(row):
        xml = ['<tr>']
        for i, col_name in enumerate(row.index):
            xml.append('  <{0}>{1}</{2}>'.format(col_name, row.iloc[i], col_name))
        xml.append('</tr>')
        return '\n'.join(xml)

    # XML buffer
    res = '<?xml version="1.0" encoding="UTF-8"?>\n'
    res += "<table>\n"
    res += '\n'.join(df.apply(row_to_xml, axis=1))
    res += "\n"
    res += "</table>"

    # if file not defined then return string
    if filename is None:
        return res

    # save to file
    with open(filename, mode, encoding="UTF-8") as f:
        f.write(res)


# add pandas.DataFrame method for save to XML
pandas.DataFrame.to_xml = to_xml


def GetFileData( filename ):
    """ Read file into pandas.DataFrame
        :param filename: ""
        :return:         pandas.DataFrame
    """
    # read data
    if filename.endswith('csv'):
        df = pandas.read_csv(filename, sep=None, engine='python')

    elif filename.endswith('xls'):
        df = pandas.read_excel(filename)

    elif filename.endswith('xlsx'):
        df = pandas.read_excel(filename)

    elif filename.endswith('json'):
        df = pandas.read_json(filename, orient='records')

    elif filename.endswith('xml'):
        df = GetFileDataXML(filename)

    else:
        raise Exception("Unsuppported")

    return df


def GetFileDataXML(filename):
    """ Read xml file with data
        :param filename:    "" file name
        :return:            pandas Dataframe
    """
    import xml.etree.ElementTree as ET
    import pandas as pd

    class XML2DataFrame:
        def __init__(self, xml_data):
            self.root = ET.XML(xml_data)

        def parse_root(self, root):
            return [self.parse_element(child) for child in iter(root)]

        def parse_element(self, element, parsed=None):
            if parsed is None:
                parsed = dict()
            for key in element.keys():
                parsed[key] = element.attrib.get(key)
            if element.text:
                parsed[element.tag] = element.text
            for child in list(element):
                self.parse_element(child, parsed)
            return parsed

        def process_data(self):
            structure_data = self.parse_root(self.root)
            return pd.DataFrame(structure_data)

    # read XMl to memory
    with open(filename, encoding="UTF-8") as f:
        xml_data = f.read()

    # parse text to XML
    xml2df = XML2DataFrame(xml_data)

    # parse XMl to pandas.DataFrame
    df = xml2df.process_data()

    return df


def get_db_connection(DatabaseName):
    """ Return DB connection for insert data to SQLite/MySQL. default: sqlite
        :param DatabaseName: ""
        :return: SqlAlchemy connection object
        See also: settings.DB_CONNECTION_STRING
    """
    from sqlalchemy import create_engine
    from .. import settings

    # connect
    engine = create_engine(settings.DB_CONNECTION_STRING)
    connection = engine.connect()

    # setup UTF-8 support
    setup_utf8_support(connection)

    return connection


def setup_utf8_support(dbc):
    """ Setup UTF-8 support
    :param dbc DBConnection
    """
    #dbc.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
