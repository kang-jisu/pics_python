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

import sys
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

okt = Okt()
 
okt.morphs     #형태소 분석
okt.nouns      #명사 분석

app = Flask (__name__)
 
CORS(app, resources={r'*': {'origins': '*'}})

def OCR(pic_data):
    print(pic_data)
    filename = secure_filename(pic_data.filename) # 업로드 된 파일의 이름이 안전한가를 확인해주는 함수이다. 해킹 공격에 대해 보안을 하고자 사용되기도 한다.
    print(filename)
    return filename


@app.route('/')
def hello_world():
    return 'Hello, World!'
 
@app.route('/main')
@app.route('/main/<int:num>') # 두개의 주소를 모두 아래있는 함수로 실행. 이중라우팅
def inputTest(num=None):
    return render_template('main.html',num=num)

@app.route('/calculate',methods=['POST'])
def calculate(num=None):
    if request.method == 'POST':
        temp = request.form['num']
    else:
        temp = None
    return redirect(url_for('inputTest',num=temp))
 
@app.route('/user/<userName>') # URL뒤에 <>을 이용해 가변 경로를 적는다
def hello_user(userName):
    print(okt.morphs(userName))
    return 'Hello, %s'%(userName)



# api 
@app.route('/file',methods=['POST'])
def getFile(file=None):
    result = {"text":None,}
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'File is missing', 404
    
        pic_data = request.files['file']
        result["text"] = OCR(pic_data)
        startDate = datetime.now().timetuple()
        endDate = datetime.now().timetuple()

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

@app.route('/cr')
def crolling():

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver_path = "./chromedriver"
    driver = webdriver.Chrome(driver_path,chrome_options=options)

    target_url = "http://www.saramin.co.kr/zf_user/tools/character-counter"                                              # target url


    key_words = [ '우리 월욜에만나!!ㅋㅋ' ]
    result = None
    for word in key_words:
        driver.get(target_url)
        search_window = driver.find_element_by_name("content")  # search window

        search_window.send_keys(word)
        #맞춤법 검사버튼 클릭
        btn = driver.find_element_by_id("spell_check")
        btn.click();

        time.sleep(1)

        #맞춤법 일괄 변경 클릭
        editBtn = driver.find_element_by_id("spell_done_all")
        #print(editBtn)
        #editBtn.click();
        editBtn.send_keys('\n')  

        time.sleep(0.5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        result = str(soup.select("#checker_preview"))

        #태그 제거
        result = re.sub('<.+?>', '', result, 0).strip();

        print(result)
        # result = driver.find_element_by_class_name("wrong solved")
        # print(result)


        print()

        time.sleep(2)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0')
