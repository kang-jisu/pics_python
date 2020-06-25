from flask import Flask, render_template, redirect, request, url_for
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
try:
    # The typical way to import flask-cors
    from flask_cors import CORS
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_cors import cross_origin

from konlpy.tag import Okt
import os
import sys
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from object_detection.image_to_text import ImageToText
from extractTime import todayTomorrow
from extractDateNew import extractDate
from pytz import timezone

from keras.models import load_model
from tensorflow import Graph, Session

from NLP.entity_sentiment_v4 import DateTimeSentimentAnalyzer
from NLP.date_time_tagger import dt_select
from NLP.preprocessor import preprocess

import numpy as np
from gensim.models.wrappers import FastText
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.models import load_model


itt = ImageToText() # 말풍선 인식 모델
dtsa = DateTimeSentimentAnalyzer(False)

def extractDateTIme(status,text):
    # status : "DATETIME","DATE","TIME"으로 구분

    if status=="DATETIME":
        #extractDate+time 따로 불러와서 실행하면됨
        resDate = extractDate(text[0])
        resTime = todayTomorrow(text[1])
        return [resDate[0],resDate[1],resDate[2],resTime[1],resTime[2]]
    elif status=="DATE":
        resDate = extractDate(text[0])
        return [resDate[0],resDate[1],resDate[2],0,0]
    elif status=="TIME":
        #extracttime에서 오늘인지 내일인지 구분해줌
        resTime = todayTomorrow(text[1])
        tmp = None
        if resTime[0] == 0: # 오늘
            tmp = datetime.now(timezone('Asia/Seoul'))
        else : # 내일
            tmp = datetime.now(timezone('Asia/Seoul')) + timedelta(days=1)
        tmp = tmp.timetuple()
        result = [tmp.tm_year,tmp.tm_mon,tmp.tm_mday, resTime[1],resTime[2]]
        return result

print("크롬실행중")


options = webdriver.ChromeOptions()
options.add_argument('headless')

driver_path = "./chromedriver"
driver = webdriver.Chrome(driver_path,chrome_options=options)

target_url = "http://www.saramin.co.kr/zf_user/tools/character-counter"                                              # target url
driver.get(target_url)
search_window = driver.find_element_by_name("content")  # search window

print("크롬실행!")

app = Flask (__name__)

config = tf.ConfigProto()
print("session")
sess = tf.Session(config=config)
set_session(sess)

print("graph")
graph = tf.get_default_graph()
#의도(질문인지 아닌지) 확인하는 코드
print("model_ft")
global modefl_ft
model_ft = FastText.load_fasttext_format('/home/ec2-user/model/model_drama.bin')

print("model_fci")
global model_fci
model_fci  = load_model('/home/ec2-user/model/rec_self_char_dense_drop-24-0.8882.hdf5')
global wdim
wdim=100
reg_ex = re.compile(r'.*[?]([-=+,#/;:\\^$.@*\s\'\"~%&!\(\)\<\>])*$')


def featurize_charrnn_utt(corpus,maxcharlen):
    rec_total = np.zeros((1,maxcharlen, wdim))
    s = corpus
    for j in range(len(s)):
        if s[-j-1] in model_ft and j<maxcharlen:
            rec_total[0,-j-1,:]=model_ft[s[-j-1]]
    return rec_total

def pred_only_text(s):
    global sess
    global graph
    with graph.as_default():
        set_session(sess)
        rec = featurize_charrnn_utt(s, 80)
        att=np.zeros((1,64))
        z = model_fci.predict([rec,att])[0]
        z = np.argmax(z)
        y = int(z)
        return z

    print("error in 3i4k")
    return 0


def is_question(s):
    m = reg_ex.match(s)
    if m:
        return True
    else:
        if pred_only_text(s) == 2:
            return True
        else:
            return False

CORS(app, resources={r'*': {'origins': '*'}})

@app.route('/main')
@app.route('/main/<int:num>') # 두개의 주소를 모두 아래있는 함수로 실행. 이중라우팅
def inputTest(num=None):
    return render_template('main.html',num=num)

# api 
@app.route('/file',methods=['POST'])
def getFile(file=None):
    result = {"text":None,}
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'File is missing', 404
    
        pic_data = request.files['file']
        result["text"] = secure_filename(pic_data.filename) 
        startYear = 2020
        startMonth = 5
        startDay = 27
        startHour = 23
        startMin = 11
        startDate = datetime(startYear,startMonth,startDay,startHour,startMin)

        endDate = startDate + timedelta(hours=1)
        endDate = endDate.timetuple()
        startDate = startDate.timetuple()

        result["startYear"]=startDate.tm_year
        result["startMonth"]=startDate.tm_mon
        result["startDay"]=startDate.tm_mday
        result["startHour"]=startDate.tm_hour
        result["startMin"]=startDate.tm_min
        result["endYear"]=endDate.tm_year
        result["endMonth"]=endDate.tm_mon
        result["endDay"]=endDate.tm_mday
        result["endHour"]=endDate.tm_hour
        result["endMin"]=endDate.tm_min
        print(result)
    return result

@app.route('/fileandcroll',methods=['POST'])
def crolling(file=None):
    result = {"text":None,}
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'File is missing', 404
    
        pic_data = request.files['file'] # 받은 파일
        filename = secure_filename(pic_data.filename) #파일 이름
        new_path = os.path.abspath(filename)  # 파일의 절대 경로
        print(new_path,'파일 생성')
        pic_data.save(new_path)

        #문장 가져오기!
        sentences = itt.image_to_text(new_path)
        print(sentences)

        result["text"] = filename


        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')

        # driver_path = "./chromedriver"
        # driver = webdriver.Chrome(driver_path,chrome_options=options)

        # target_url = "http://www.saramin.co.kr/zf_user/tools/character-counter"                                              # target url
        # driver.get(target_url)
           
        resultCroll = None
        resultText=""
        sentencesGroup = ""
        if len(sentences)==0:
            resultText="12시"
        else :
            sentencesGroup = "\n".join(sentences)
            # # 크롤링
            print("크롤링")
            search_window.clear()
            search_window.send_keys(sentencesGroup)
            #맞춤법 검사버튼 클릭
            btn = driver.find_element_by_id("spell_check")
            btn.click()

            time.sleep(0.5)

            #맞춤법 일괄 변경 클릭
            editBtn = driver.find_element_by_id("spell_done_all")
            #print(editBtn)
            #editBtn.click();
            editBtn.send_keys('\n')  

            time.sleep(0.3)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            resultCroll = str(soup.select("#checker_preview"))

            #태그 제거
            resultText = re.sub('<.+?>', '', resultCroll, 0).strip();
            # print(resultText)

            successBtn = driver.find_element_by_id("spell_completion")
            successBtn.send_keys('\n')

        if os.path.isfile(new_path):
            os.remove(new_path)
            print(new_path,'파일 삭제')

        status = "DATETIME"
        # text = "다음주 일요일 4시 반"

        print(resultText)
        resultText = resultText.replace("[","")
        resultText=resultText.replace("]","")
        
        text = resultText.split("\n")
        print(text)
        text = dtsa.split_sentence_with_s(text)
        text = preprocess(text)
        print(text)
        is_question_list = []
        for tx in text:
            is_question_list.append(is_question(tx))
        result_dt = dt_select(dtsa.entity_sentiment_analyze(text, is_question_list))
        print(result_dt)
        
        if result_dt[0]!="" and result_dt[1]!="":
            status="DATETIME"
        elif result_dt[0]!="" and result_dt[1]=="":
            status="DATE"
        elif result_dt[0]=="" and result_dt[1]!="":
            status="TIME"
        ext = extractDateTIme(status,result_dt)
        print(ext)

        startDate = datetime(ext[0],ext[1],ext[2],ext[3],ext[4])

        endDate = startDate + timedelta(hours=1)
        endDate = endDate.timetuple()
        startDate = startDate.timetuple()

        result["startYear"]=startDate.tm_year
        result["startMonth"]=startDate.tm_mon
        result["startDay"]=startDate.tm_mday
        result["startHour"]=startDate.tm_hour
        result["startMin"]=startDate.tm_min
        result["endYear"]=endDate.tm_year
        result["endMonth"]=endDate.tm_mon
        result["endDay"]=endDate.tm_mday
        result["endHour"]=endDate.tm_hour
        result["endMin"]=endDate.tm_min
        print(result)

    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0')


driver.quit()
