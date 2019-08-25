import os

BrainID   = "Brain01"   # DATABASE
TABLENAME = "TEST"      # DB TABLE
USERNAME  = "admin"     # HTTP user name
PASSWORD  = "pwd123"    # HTTP password

# base dir. path to app root folder
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER       = os.path.join(BASE_DIR, 'uploads')

# DB connection string in SQLAlchemy format
# for SQLite
sqlitedb = os.path.abspath(os.path.join(BASE_DIR, BrainID + '.sqlite3'))  # full path to sqlite3 db file
DB_CONNECTION_STRING = 'sqlite:///{}'.format(sqlitedb)
# for MySQL
#DB_CONNECTION_STRING = 'mysql://testuser:testpassword@localhost/{}'.format(BrainID)

# allowed extensions. supported extension used in receive http form validation
ALLOWED_EXTENSIONS  = {'json', 'csv', 'xls', 'xlsx', 'xml'}

# DB table columns
TABLE_COLS = ['ID:PRIMARYKEYAUTO', 'SomeNumbers5:FLOAT', 'OneDate:DATETIME', 'SomeTagSingle26:TEXT']

ColumnsNameInput = ["SomeNumbers5" , "OneDate"]
ColumnsNameOutput = ["SomeTagSingle26"]

ColumnType = {
    "SomeNumbers5"    : "NUMERIC",
    "OneDate"         : "DATETIME",
    "SomeTagSingle26" : "TAGS"
}

# available types
types = [
    "NUMERICAL",
    "DATE",
    "DATETIME",
    "TIME",
    "TAGS",     # TEXT
    "BOOLEAN",  # NUMERICAL,
    "OPTIONS",  # TEXT
]

