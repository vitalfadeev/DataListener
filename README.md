## About
Flask app.
- receive csv/xls/json/xml
- auth via username/password: ?username=test&password=test
- sqlite/mysql
- `pandas`  as backend for reading csv/xls/json/xml: 
- emission DB table data as csv


### install
see, please `1-install.sh`

### tests
see, please `datalistener/test.py`

### settings
see, please `datalistener/settings.py` and `datalistener/my.cnf`  

### HTTP usage
- POST /store?username=test&password=test&file=<data>
- GET /read?username=test&password=test&format=csv

#### debugging
- POST /store-dev?username=test&password=test
- GET /read-dev?username=test&password=test
- GET /

