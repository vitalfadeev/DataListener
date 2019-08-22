import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BrainID = "Brain01"
USERNAME = "admin"
PASSWORD = "pwd123"
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

ColumnsNameInput = ["Col2" , "Col3"]
ColumnsNameOutput = ["Col1"]
ColumnType = {
    "Col1":"NUMERIC",
    "Col2":"DATETIME",
    "Col3":"TAGS"
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

