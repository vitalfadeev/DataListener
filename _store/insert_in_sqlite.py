#
#
#
def sqlite_db():
    import sqlite3

    conn = sqlite3.connect("test.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()

    #
    cursor.execute("""CREATE TABLE test (
                      id INTEGER PRIMARY KEY ASC, 
                      Col1 REAL, 
                      Col2 TEXT, 
                      Col3 TEXT 
                      )
                   """)
