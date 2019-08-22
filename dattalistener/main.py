from . import sqlinterface

db = sqlinterface.SQLInterface()

TableName = "test"
db.SqlCreateTable( TableName, ["ID:PRIMARYKEYAUTO", "Col1:FLOAT", "Col2:DATETIME", "Col3:TEXT"] )


DMY = "DMY"
MDY = "MDY"


def DataStoreInSql( DatabaseName, TableName, DataArrayToWrite, SettingFormatDate = MDY ):
    c = db.SqlExecuteManyInsert( TableName, DataArrayToWrite )

    LastPrimaryKeyWritten = c.lastrowid

    return LastPrimaryKeyWritten


def send_csv():
    pass


def auth():
    # Verify Authentication user
    pass


def extract_columns_names( DataSource ):
    """
		Json,xml : take names from Key/Pair
		CSV/Excel : take names from the first line of file
		http-post data (key=value) & http-get data (key=value
    """
    pass


def parse_data():
    """
    Parse all data line(s) and store each lines into Sql database Table TEST (Note ID column is automatically added by mysql)
    If some columns are not in database , to skip columns and print a warning
    """
    pass


def DataReadFromSql( DatabaseName, TableName, ExportLinesAfterPrimaryKey, FormatOutput ):
    DataArrayExported = []
    return DataArrayExported

