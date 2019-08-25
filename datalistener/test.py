# send
# http://localhost:5000/store

# receive
# http://localhost:5000/read?databasename=format=csv
# http://localhost:5000/read?databasename=format=xls
# http://localhost:5000/read?databasename=format=json
# http://localhost:5000/read?databasename=format=xml

import os
import requests
from requests.auth import HTTPBasicAuth


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_store():
    """ Test upload csv
    """
    print("Store data: ", end="")
    r = requests.post(
        'http://localhost:5000/store',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        files={
            'file': open(os.path.join(BASE_DIR, 'tests', 'test-2.csv'), 'rb')
        })

    if r.status_code == 200:
        print("[ OK ]")
        print("  text:", r.text)
    else:
        print("[FAIL]")
        print("  code:", r.status_code)
        print("  text:", r.text)

    r.close()


def test_read_csv():
    """ Test download csv
    """
    print("Read data: ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        params = {
            'format'  : 'csv',
        },
        stream=True)

    if r.status_code == 200:
        print("[ OK ]")
        write_file(r)

    else:
        print("[FAIL]")
        print("  text:", r.text)

    r.close()


def test_read_xls():
    """ Test download xls
    """
    print("Read data: ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        params = {
            'format'  : 'xls',
        },
        stream=True)

    if r.status_code == 200:
        print("[ OK ]")
        write_file(r)

    else:
        print("[FAIL]")
        print("  text:", r.text)

    r.close()


def test_read_json():
    """ Test download json
    """
    print("Read data: ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        params = {
            'format'  : 'json',
        },
        stream=True)

    if r.status_code == 200:
        print("[ OK ]")
        write_file(r)

    else:
        print("[FAIL]")
        print("  text:", r.text)

    r.close()


def test_read_xml():
    """ Test download ml
    """
    print("Read data: ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        auth=HTTPBasicAuth('admin', 'pwd123'),
        params = {
            'format'  : 'xml',
        },
        stream=True)

    if r.status_code == 200:
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


if __name__ == "__main__":
    test_store()
    test_read_csv()
    test_read_xls()
    test_read_json()
    test_read_xml()
    test_read_csv_from(10)

