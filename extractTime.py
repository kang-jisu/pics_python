import re
from pytz import timezone
from datetime import timedelta, datetime

#한국어 시간 인식
korHours = ['한', '두', '세', '네', '다섯', '여섯', '일곱', '여덟', '아홉', '열', '열한', '열두']
korMinutes = ['일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십']

def todayTomorrow(text):
    date = 0 # 0: 오늘 1:내일

    #오전오후
    ampm = re.findall('오전|오후', text)
    #한국어 시
    textHour = re.findall('한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|열한|열두', text)
    #한국어 분
    textMinute = re.findall('일|이|삼|사|오|육|칠|팔|구|십', text)
    #숫자 시, 분
    textTime = re.findall('\d{1,2}', text)
    #30분 => 반
    textHalf = re.findall('반', text)

    hour = None
    minute = 0
    if len(textMinute) > 0:
        minLen = len(textMinute)
        #십 => 10
        if minLen == 1 and textMinute[minLen - 1] == "십":
            minute = 10
        #십일~십구 => 11이상 19이하인 경우에, 10 인식
        if minLen == 2 and textMinute[minLen - 2] == "십":
            minute += 10
        for idx, val  in enumerate(korMinutes):
            #일, 이, 삼, 사, 오, 육, 칠, 팔, 구 => 맨 뒷자리 인식
            if val == textMinute[minLen-1] and val != "십":
                minute += idx + 1
            #이십, 삼십, 사십, 오십, 육십 => 십으로 떨어지는 경우인데 두글자
            if minLen - 2 >= 0 and val == textMinute[minLen-2] and textMinute[minLen-1] == "십":
                minute += (idx + 1) * 10
            #이십일, 이십이,...  오십구 => 맨 앞자리 인식
            if minLen - 3 >= 0 and val == textMinute[minLen-3]:
                minute += (idx + 1) * 10

    if len(textHour) > 0:
        if len(textHour) == 1:
            korHour = textHour[0]
        if len(textHour) == 2:
            korHour = textHour[0] + textHour[1]

        for idx, val in enumerate(korHours):
            if val == korHour:
                if len(ampm) == 1 and ampm[0] == "오전":
                    hour = idx + 1
                else:
                    if len(ampm) == 1 and ampm[0]=="오후" and val[0]=="열":
                        if val =="열두": hour = idx+1 # 오후 열두시는 12시
                        else : hour = idx + 13 # 오후 열~열한시
                    elif(val[0]=="열"):
                        hour = idx + 1 # 그냥 열~열두시는 오전으로쳐야함
                    else :
                        hour = idx + 13 # 나머지
                break

    if hour is not None and len(textTime) == 1:
        minute = int(textTime[0])

    if hour is None and len(textTime) > 0:
        # 오전 오후 명시된 경우
        if len(ampm) == 1 and ampm[0] == "오전":
            hour = int(textTime[0])

        elif len(ampm) == 1 and ampm[0] == "오후":
            hour = int(textTime[0]) + 12

    # 10시 이상 12시 이하면 오전, 0~9시 오후 처리
        elif (int(textTime[0]) >= 10 and int(textTime[0]) <= 12) or int(textTime[0]) >=13:
            hour = int(textTime[0])
        else:
            hour = int(textTime[0]) + 12
        # 분을 숫자로 표현한경우
        if len(textTime) == 2:
            minute = int(textTime[1])

    #반
    if len(textHalf) == 1:
        minute = 30
    now = datetime.now(timezone('Asia/Seoul'))
    nowHour = now.timetuple().tm_hour
    nowMin = now.timetuple().tm_min

    if nowHour-hour >0: # 명시된 시간이 지금 시간보다 지난상태
        date = 1
    elif nowHour-hour==0:
        if nowMin - minute >= 0: # 명시된 시간이 지금 시간보다 지난상태
            date = 1
        else :
            date = 0
    else : # 오늘
        date = 0
    return [date,hour,minute]


# text = "오전 3시 19분"
# print(todayTomorrow(text))
