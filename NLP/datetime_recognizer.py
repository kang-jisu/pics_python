
#-*- coding:utf-8 -*-
import urllib3
import json
import os
import re
 
def datetime_recognizer(text):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"
    accessKey = os.getenv('accessKey')
    analysisCode = "ner"
    
    requestJson = {
        "access_key": accessKey,
        "argument": {
            "text": text,
            "analysis_code": analysisCode
        }
    }
    
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )
    
    json_data = json.loads(response.data.decode('utf-8'))
    named_entity = json_data['return_object']['sentence'][0]['NE']
    date_time_list = []

    month = re.compile(r'(?:\d|[일이삼사오유육칠팔구십시]){1,2}(?:월)')
    date = re.compile(r'(?:\d|[일이삼사오육칠팔구십]){1,2}(?:일)')
    day = re.compile(r'[월화수목금토일](?:요일)')

    hour = re.compile(r'(?:\d|[한두세네열]|다섯|여섯|일곱|여덟|아홉){1,3}\s*(?:시)(?:반)?')
    minute = re.compile(r'(?:\d|[일이삼사오육칠팔구십]){1,3}\s*(?:분)')
    
    for i in named_entity:
        if i['type'][:2] == 'DT':
            time_list = hour.findall(i['text'])
            time_list += minute.findall(i['text'])
            if len(time_list) != 0:
                for ti in time_list:
                    date_time_list.append((ti, 'TI_OTHERS'))
            else:
                dt_list = i['text'].split(' ')
                for dt in dt_list:
                    date_time_list.append((dt, i['type']))

        elif i['type'][:2] == 'TI':
            date_time_list.append((i['text'], i['type']))

        else:
            date_list = month.findall(i['text'])
            date_list += date.findall(i['text'])
            date_list += day.findall(i['text'])

            time_list = hour.findall(i['text'])
            time_list += minute.findall(i['text'])

            for i in date_list:
                date_time_list.append((i, 'DT_OTHERS'))
            
            for i in time_list:
                date_time_list.append((i, 'TI_OTHERS'))
            
    return date_time_list
