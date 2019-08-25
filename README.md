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
