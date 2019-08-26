# send
# http://localhost:5000/store

# receive
# http://localhost:5000/read?databasename=format=csv
# http://localhost:5000/read?databasename=format=xls
# http://localhost:5000/read?databasename=format=json
# http://localhost:5000/read?databasename=format=xml
# http://localhost:5000/read?databasename=format=csv&from_id=10

import os
import requests
from requests.auth import HTTPBasicAuth


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_test_table():
    """ Create test database. And test table.
    See also: settings.py
    """
    from datalistener import settings
    from sqlinterface import SQLInterface

    # init sqli interface
    db = SQLInterface(settings.DB_CONNECTION_STRING)

    # create database
    db.SqlDropDatabase(settings.BrainID)
    db.SqlCreateDatabase(settings.BrainID)
    db.UseDatabase(settings.BrainID)

    # create table
    # use types from settings.
    ctypes = settings.ColumnType
    # add ID as primary key
    ctypes['ID'] = "PRIMARYKEYAUTO"
    # to string
    stypes = [ "{}:{}".format(cname, ctype) for (cname, ctype) in settings.ColumnType.items() ]
    # create table
    db.SqlCreateTable(settings.TABLENAME, stypes)



def test_store(format):
    """ Test upload csv
    """
    print("test_store({}) ".format(format), end="")

    # make request
    r = requests.post(
        'http://localhost:5000/store',          # Flask url
        auth=HTTPBasicAuth('admin', 'pwd123'),  # http basic auth username/password
        files={                                 # file to upload
            'file': open(os.path.join(
                BASE_DIR, 'tests', 'test-2.{}'.format(format)),
                'rb'
            )
        })

    # check response
    if r.status_code == 200:                    # 200 - OK
        print("[ OK ]")
        print("  last id:", r.text)
    else:
        print("[FAIL]")
        print("  code:", r.status_code)
        print("  text:", r.text)

    r.close()


def test_store_http_get():
    """ Test upload csv
    """
    print("test_store_http_get() ", end="")

    # make request
    r = requests.get(
        'http://localhost:5000/store',          # Flask url
        auth=HTTPBasicAuth('admin', 'pwd123'),  # http basic auth username/password
        params={                                # HTTP GET URL params
            'SomeNumbers5': 1
        }
    )

    # check response
    if r.status_code == 200:
        print("[ OK ]")
        print("  last id:", r.text)
    else:
        print("[FAIL]")
        print("  code:", r.status_code)
        print("  text:", r.text)

    r.close()


def test_store_http_post():
    """ Test upload csv
    """
    print("test_store_http_post() ", end="")

    # make request
    r = requests.post(
        'http://localhost:5000/store',          # Flask url
        auth=HTTPBasicAuth('admin', 'pwd123'),  # http basic auth username/password
        data={                                  # HTTP GET URL params
            'SomeNumbers5': 2
        }
    )

    # check response
    if r.status_code == 200:
        print("[ OK ]")
        print("  last id:", r.text)
    else:
        print("[FAIL]")
        print("  code:", r.status_code)
        print("  text:", r.text)

    r.close()


def test_read(format):
    """ Test download csv
    """
    print("test_read({}): ".format(format), end="")

    # make request
    r = requests.get(
        'http://localhost:5000/read',           # Flask url
        auth=HTTPBasicAuth('admin', 'pwd123'),  # http basic username/password
        params = {
            'format'  : format,
        },
        stream=True)

    # check response
    if r.status_code == 200:                    # 200 - OK
        print("[ OK ]")
        write_file(r)

    else:
        print("[FAIL]")
        print("  text:", r.text)

    r.close()



def write_file(r):
    """ Handle downloaded file. Save to temporary folder. Name: DataReadFromSql-<RANDOM>.csv
        :param r: Request
        :return:
    """
    # get file name
    import re
    d = r.headers['content-disposition']
    filename = re.findall("filename=(.+)", d)[0]

    # save file
    import tempfile
    fd, outfile = tempfile.mkstemp(prefix="DataReadFromSql-", suffix="-" + filename )
    with open(outfile, 'wb') as f:
        for chunk in r:
            f.write(chunk)
    os.close(fd)

    return outfile


def test_local():
    """ Test inserting local file to DB
    """
    from datalistener import settings
    from app import ProcessFile
    ffname = os.path.join(settings.BASE_DIR, 'tests', 'test-2.csv')
    ProcessFile(ffname)


def test_read_csv_from(from_id):
    """ Test download csv
    """
    print("Read data from:", from_id, " ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        params = {
            'from_id' : from_id,
            'format'  : 'csv',
        },
        stream=True)

    if r.status_code == 200:
        # get file
        outfile = write_file(r)

        # check ID
        import pandas
        df = pandas.read_csv(outfile, sep="\t") # read csv file to DataFrame

        if df.iloc[0]['ID'] == from_id: # check first row, column named 'ID'
            print("[ OK ]")
        else:
            print("[FAIL]")

    else:
        print("[FAIL]")
        print("  text:", r.text)

    r.close()


def test_store_unicode():
    # тест-测试
    """ Test upload csv
    """
    print("test_store_unicode()", end="")

    # make request
    r = requests.post(
        'http://localhost:5000/store',          # Flask url
        auth=HTTPBasicAuth('admin', 'pwd123'),  # http basic auth username/password
        files={                                 # file to upload
            'file': open(os.path.join(
                BASE_DIR, 'tests', 'test-unicode.csv'),
                'rb'
            )
        })

    # check response
    if r.status_code == 200:                    # 200 - OK
        print("[ OK ]")
        print("  last id:", r.text)
    else:
        print("[FAIL]")
        print("  code:", r.status_code)
        print("  text:", r.text)

    r.close()


if __name__ == "__main__":
    # create TEST table
    create_test_table()

    # test store data
    test_store('csv')
    test_store('xls')
    test_store('xlsx')
    test_store('json')
    test_store('xml')

    # test store via HTTP GET
    test_store_http_get()
    test_store_http_get()
    test_store_http_get()

    # test store via HTTP POST
    test_store_http_post()
    test_store_http_post()
    test_store_http_post()

    # test read data
    test_read('csv')
    test_read('xls')
    test_read('xlsx')
    test_read('json')
    test_read('xml')

    # test read data from ID = 10
    test_read_csv_from(10)

    # test unicode
    # тест-测试
    test_store_unicode()
    test_read('csv')
