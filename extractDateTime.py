from extractTime import todayTomorrow
from extractDateNew import extractDate
import re
from pytz import timezone
from datetime import timedelta, datetime


# now = datetime.now(timezone('Asia/Seoul')).timetuple()
# nowYear = now.tm_year
# nowMonth = now.tm_mon
# nowDay = now.tm_mday
# nowHour = now.tm_hour
# nowMin = now.tm_min

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

# MAIN 함수

status = "DATETIME"
# status = "TIME"
# status = "DATE"
text = "내일 세시"
# text = "다음주 금요일 "
# text= "2시"
result = extractDateTIme(status,text)
print(text)
print(result)
