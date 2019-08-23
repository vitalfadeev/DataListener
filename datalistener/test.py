# send
# http://localhost:5000/store-dev?username=admin&password=pwd123

# receive
# http://localhost:5000/read?username=admin&password=pwd123&databasename=Brain01&tablename=TEST&exportlines=5&formatoutput=csv&submit=Read&format=csv
# http://localhost:5000/read?username=admin&password=pwd123&databasename=Brain01&tablename=TEST&exportlines=5&formatoutput=csv&submit=Read&format=xls
# http://localhost:5000/read?username=admin&password=pwd123&databasename=Brain01&tablename=TEST&exportlines=5&formatoutput=csv&submit=Read&format=json
# http://localhost:5000/read?username=admin&password=pwd123&databasename=Brain01&tablename=TEST&exportlines=5&formatoutput=csv&submit=Read&format=xml

import os
import requests


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_store():
    """ Test upload csv
    """
    print("Store data: ", end="")
    r = requests.post(
        'http://localhost:5000/store',
        data = {
            'username': 'admin',
            'password': 'pwd123',
        },
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


def test_read():
    """ Test download csv
    """
    print("Read data: ", end="")
    r = requests.get(
        'http://localhost:5000/read',
        params = {
            'username': 'admin',
            'password': 'pwd123',
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


def write_file(r):
    """ Handle downloaded file. Save to temporary folder. Name: DataReadFromSql-<RANDOM>.csv
        :param r: Request
        :return:
    """
    import tempfile
    fd, outfile = tempfile.mkstemp(prefix="DataReadFromSql-", suffix=".csv")
    with open(outfile, 'wb') as f:
        for chunk in r:
            f.write(chunk)
    os.close(fd)


def test_local():
    """ Test inserting local file to DB
    """
    from datalistener import settings
    from app import ProcessFile
    ffname = os.path.join(settings.BASE_DIR, 'tests', 'test-2.csv')
    ProcessFile(ffname)


if __name__ == "__main__":
    test_store()
    test_read()

