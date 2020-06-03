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
itt = ImageToText() # 말풍선 인식 모델 학습

def extractDateTIme(status,text):
    # status : "DATETIME","DATE","TIME"으로 구분

    if status=="DATETIME":
        #extractDate+time 따로 불러와서 실행하면됨
        resDate = extractDate(text)
        resTime = todayTomorrow(text)
        return [resDate[0],resDate[1],resDate[2],resTime[1],resTime[2]]
    elif status=="DATE":
        resDate = extractDate(text)
        return [resDate[0],resDate[1],resDate[2],0,0]
    elif status=="TIME":
        #extracttime에서 오늘인지 내일인지 구분해줌
        resTime = todayTomorrow(text)
        tmp = None
        if resTime[0] == 0: # 오늘
            tmp = datetime.now(timezone('Asia/Seoul'))
        else : # 내일
            tmp = datetime.now(timezone('Asia/Seoul')) + timedelta(days=1)
        tmp = tmp.timetuple()
        result = [tmp.tm_year,tmp.tm_mon,tmp.tm_mday, resTime[1],resTime[2]]
        return result

app = Flask (__name__)
 
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


        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        driver_path = "./chromedriver"
        driver = webdriver.Chrome(driver_path,chrome_options=options)

        target_url = "http://www.saramin.co.kr/zf_user/tools/character-counter"                                              # target url


        key_words = sentences
        resultCroll = None
        resultText=""
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
            resultCroll = str(soup.select("#checker_preview"))

            #태그 제거
            resultCroll = re.sub('<.+?>', '', resultCroll, 0).strip();

            print(resultCroll)
            resultText+=resultCroll+" "
            # result = driver.find_element_by_class_name("wrong solved")
            # print(result)


            print()

            # time.sleep(2)
        if os.path.isfile(new_path):
            os.remove(new_path)
            print(new_path,'파일 삭제')
        status = "DATETIME"
        # text = "다음주 일요일 4시 반"
        text = resultText
        ext = extractDateTIme(status,text)
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
