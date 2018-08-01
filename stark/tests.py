from django.test import TestCase

# Create your tests here.
import json
from datetime import datetime
from datetime import date
class MyJson(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,datetime):
            return o.strftime('%Y-%m-%d %H-%M-%S')
        elif isinstance(o,date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self,o)
dic={'time':datetime.now(),'time1':date.today(),'Chinese':'哈哈'}
json.dumps(dic,cls=MyJson,ensure_ascii=False)