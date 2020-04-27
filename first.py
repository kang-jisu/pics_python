from flask import Flask, render_template, redirect, request, url_for
from werkzeug.utils import secure_filename
import datetime
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
    result = {"text":"error","date":None}
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'File is missing', 404
    
        pic_data = request.files['file']
        result["text"] = OCR(pic_data)
        result["date"]=datetime.datetime.now()
        print(result)
    return result
 


if __name__ == "__main__":
    app.run(host='0.0.0.0')