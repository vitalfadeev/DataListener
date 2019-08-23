import os

DRIVER = "sqlite" # sqlite | mysql

BrainID   = "Brain01"
TABLENAME = "TEST"
USERNAME  = "admin"
PASSWORD  = "pwd123"

BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER       = os.path.join(BASE_DIR, 'uploads')

ALLOWED_EXTENSIONS  = {'json', 'csv', 'xls', 'xlsx', 'xml'}

TABLE_COLS = ['ID:PRIMARYKEYAUTO', 'SomeNumbers5:FLOAT', 'OneDate:DATETIME', 'SomeTagSingle26:TEXT']

ColumnsNameInput = ["SomeNumbers5" , "OneDate"]
ColumnsNameOutput = ["SomeTagSingle26"]

ColumnType = {
    "SomeNumbers5"    : "NUMERIC",
    "OneDate"         : "DATETIME",
    "SomeTagSingle26" : "TAGS"
}

types = [
    "NUMERICAL",
    "DATE",
    "DATETIME",
    "TIME",
    "TAGS",     # TEXT
    "BOOLEAN",  # NUMERICAL,
    "OPTIONS",  # TEXT
]

