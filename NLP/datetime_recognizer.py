
#-*- coding:utf-8 -*-
import urllib3
import json
 
def datetime_recognizer(text):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"
    accessKey = "ACCESSKEY를 추가하세요"
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
    for i in named_entity:
        if i['type'][:2] == 'DT':
            dt_list = i['text'].split(' ')
            for dt in dt_list:
                date_time_list.append((dt, i['type']))

        elif i['type'][:2] == 'TI':
            date_time_list.append((i['text'], i['type']))

        elif i['type'][:2] == 'QT':
            if '시' in i['text'] or '분' in i['text'] or '반' in i['text']:
                date_time_list.append((i['text'], 'TI_OTHERS'))

    return date_time_list
