import os

BrainID   = "Brain01"   # DATABASE
TABLENAME = "TEST"      # DB TABLE
USERNAME  = "admin"     # HTTP user name
PASSWORD  = "pwd123"    # HTTP password

# base dir. path to app root folder
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER       = os.path.join(BASE_DIR, 'uploads')

# DB connection string in SQLAlchemy format
# for MySQL
DB_CONNECTION_STRING = 'mysql://testuser:testpassword@localhost/{}'.format(BrainID)

# allowed extensions. supported extension used in receive http form validation
ALLOWED_EXTENSIONS  = {'json', 'csv', 'xls', 'xlsx', 'xml'}

# DB table columns. 'ID' - PRIMARY KEY
ColumnType = {
    "SomeNumbers5"      : "NUMERIC",
    "OneDate"           : "DATETIME",
    "SomeTagSingle26"   : "TAGS",
}

ColumnsNameInput  = ["SomeNumbers5", "OneDate"]
ColumnsNameOutput = ["SomeTagSingle26"]

# available types
TYPES = [
    "NUMERICAL",
    "DATE",
    "DATETIME",
    "TIME",
    "TAGS",     # TEXT
    "BOOLEAN",  # NUMERICAL,
    "OPTIONS",  # TEXT
]

