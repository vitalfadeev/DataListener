## About
Flask app.
- receive csv/xls/json/xml
- auth via basic http auth username/password
- sqlite/mysql
- `pandas`  as backend for reading csv/xls/json/xml: 
- emission DB table data as csv


### install
see, please `1-install.sh`

### tests
see, please `datalistener/test.py`

exmaple files (csv, xls, xlsx, json, xml) in forlder `datalistener/tests/`

### settings
see, please `datalistener/settings.py` and `datalistener/my.cnf`  

### HTTP usage
- POST /store?file=<data>
- GET /read?format=csv
- GET /read?format=csv&from_id=10

### Formats
#### CSV
TAB delimited

    OneDate SomeTagSingle26 OneTime SomeTagsMultiples       OneDateTime     SomeNumbers5    SomeNumbers26   TagWeighted7    SomeTagSingle10
    10.08.2020       Djibouti       12:30   white/red;blue  10.05.05 12:50  1       100     Cat=0.5  Estonia

#### JSON
    {
      "OneDate":{"0":"10.08.2020"},
      "SomeNumbers5":{"0":1},
      "SomeTagSingle26":{"0":"\u00a0Djibouti"}
    }

#### XML
    <?xml version="1.0" encoding="UTF-8"?>
    <table>
    <tr>
      <OneDate>10.08.2020</OneDate>
      <SomeNumbers5>1</SomeNumbers5>
      <SomeTagSingle26> Djibouti</SomeTagSingle26>
    </tr>
    </table>

#### XLS/XLSX
- First sheet
- First row: column names
- All next rows: data


    OneDate       SomeTagSingle26  OneTime
    10.08.2020    Djibouti         12:30

