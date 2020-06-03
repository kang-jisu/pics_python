
#-*- coding:utf-8 -*-
import urllib3
import json
import calendar
import re
import math

from pytz import timezone
from datetime import timedelta, datetime

def change_num(text):
    tlen = len(text)
    result = 1
    if tlen==1:
        if text=="십": result = 10
        if text=="유": result = 6
        if text=="시": result = 10
        else : result = "일이삼사오육칠팔구".index(text) +1
    else:
        if bool(re.search(r"삼십",text)): # 30
            if text=="삼십": result = 30
            else : result = 31
        
        elif bool(re.search(r"이십",text)): # 20
            if text=="이십": result = 20
            else :
                result = 20
                result += "일이삼사오육칠팔구".index(text[2])+1
        else:
            result = 10
            result += "일이삼사오육칠팔구".index(text[1])+1
    
    return int(result)
    
# 마지막주가 일요일일때는 뭔ㄱ, , 다른처리해주어댜ㅗ리듯
# def get_last_week_no(y, m, d):  
#     target = datetime(y,m,d,0,0)
#     firstday = target.replace(day=1)
#     if target.weekday()==6:
#         origin = firstday + timedelta(days=6-firstday.weekday())
#         return (math.floor(((target - origin).days) / 7 + 1))-1
#     if firstday.weekday() == 0:
#         origin = firstday 
#     elif firstday.weekday() < 3:
#         origin = firstday - timedelta(days=firstday.weekday() + 1)+ timedelta(days=1)
#     else:
#         origin = firstday + timedelta(days=6-firstday.weekday())
#     return math.floor(((target - origin).days) / 7 + 1)


def get_week_no(y, m, d):  

    target = datetime(y,m,d,0,0)
    firstday = target.replace(day=1)
    if firstday.weekday() == 0:
        origin = firstday 
    elif firstday.weekday() < 3:
        origin = firstday - timedelta(days=firstday.weekday() + 1)+ timedelta(days=1)
    else:
        origin = firstday + timedelta(days=6-firstday.weekday())
    return math.floor(((target - origin).days) / 7 + 1)



def get_day_from_weekday(y, m, week,day):
    # print(y,"년",m,"월",week,"째주","월화수목금토일"[day],"요일")
    firstday = calendar.weekday(int(y),int(m),int(1)) # 첫날의 월~일 인덱스 0 : 월 6 : 일
    if firstday == 0: # 월요일
        origin = 1
        return [0,origin+ (week-1)*7 + day]
    elif firstday < 4: # 화,수,목
        lastday_premonth = 31
        if m==1:
            lastday_premonth = calendar.monthrange(y-1,12)[1]
        else:
            lastday_premonth = calendar.monthrange(y,int(m)-1)[1]
        lastday_premonth = lastday_premonth-firstday  # 전 달의 마지막 일요일 
        result = lastday_premonth + (week-1)*7+day +1
        return [-1,result]
    else: # 금,토,일 -> 다음주 월?요일이 첫째주 기준
        origin = 1 + 6-firstday+1
        return [0,origin+ (week-1)*7 + day]



special_day = ["신정","삼일절","어린이날","어린이 날","근로자의 날","근로자의날","어버이날","어버이 날","스승의날","스승의 날","현충일","제헌절","광복절","개천절","한글날","크리스마스","성탄절","화이트데이","발렌타인데이","빼빼로데이"]
special_day_value = ["01 01","03 01","05 05","05 05","05 01","05 01","05 08","05 08","05 15","05 15","06 06","07 17","08 15","10 03","10 09","12 25","12 25","03 14","02 14","11 11"]


def extractDate(text):
    startDate = datetime.now(timezone('Asia/Seoul')).timetuple()
    thisyear= startDate.tm_year
    thismonth= startDate.tm_mon
    # thismonth=12
    today = startDate.tm_mday
    # today = 29
    this_last_day = calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일
    this_last_week = get_week_no(thisyear,thismonth,this_last_day)
    year = startDate.tm_year
    month = startDate.tm_mon
    # month = 12
    day = startDate.tm_mday
    # day = 29
    week = None 


    # 우선순위
    # 가까운 날짜> 기념일 > .. 

    # 가까운 날짜 : 내일, 모레
    nearDay = re.findall('내일|모레',text)
    if len(nearDay)!=0:
        addDay = 1 # 내일
        if bool(re.search(r"모레",text)):
            addDay=2
        day = today + addDay
        month = thismonth
        year = thisyear
        
        last_day= calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일
        if day > last_day :
            day = day - last_day
            month = thismonth+1
            if month > 12 :
                month = month % 12
                year = thisyear + 1  
        return [year,month,day]

    # 기념일
    specialDay = re.findall('신정|삼일절|어린이날|어린이 날|근로자의 날|근로자의날|어버이날|어버이 날|스승의날|스승의 날|현충일|제헌절|광복절|개천절|한글날|크리스마스|성탄절|화이트데이|발렌타인데이|빼빼로데이',text)
    if len(specialDay)!=0:
        for i in range (len(special_day)):
            if bool(re.match(special_day[i],specialDay[0])):
                date = special_day_value[i].split(" ")
                year = thisyear
                month = int(date[0])
                day = int(date[1])
                return [year,month,day]

    # 다음 달과 관련된 표현 : 다음달, 다음 달, 담달 
    nextMonth = re.findall('다음 달|다음달|담달',text)

    # 00월
    searchMonth = re.findall(r"\w{1,2}월",text)

    # 일 ( 일이나 월 혹시라도 여러 표현있으면 제일 뒤에 명시된거로 처리함 인덱스 (len-1))
    # 월에대한 표시 없으면 이번달 아니면 특정 달 예외처리할것
    searchDay = re.findall(r'\d{1,2}일|[가-힣]{0,2}일일|[가-힣]{0,2}이일|[가-힣]{0,2}삼일|[가-힣]{0,2}사일|[가-힣]{0,2}오일|[가-힣]{0,2}육일|[가-힣]{0,2}칠일|[가-힣]{0,2}팔일|[가-힣]{0,2}구일|[가-힣]{0,2}십일',text)
    # 첫날 마지막날 : 1일, 말일
    startEndDay = re.findall('첫 날|첫날|마지막 날|마지막날|말일',text)
    if len(searchDay)>0 or len(startEndDay)>0:

        tmp_day = None
        if len(searchDay)>0: # 일반적인 일 표현
            tmp_day = searchDay[len(searchDay)-1][0:-1]

            if bool(re.search(r"\d{1,2}",tmp_day)):
                tmp_day = int(tmp_day)
            else:
                tmp_day = change_num(tmp_day)
        
        elif bool(re.search(r"첫날",text)) or bool(re.search(r"첫 날",text)):
            tmp_day = 1

        # 월에대한 표시 있는지 확인
        if len(searchMonth)>0: # 00월 
            tmp_month = searchMonth[len(searchMonth)-1][0:-1] #5월, 오월 - > 5, 오 , 십이 
            # 문자라면 숫자로 바꿔줌 일 이 삼 사 오 육(유) 칠 팔 구 십(시) 십일 십이
            if not (tmp_month>='1' and tmp_month<='9') :
                tmp_month = change_num(tmp_month)
            else: tmp_month = int(tmp_month)

            # 달 변경. 이미 지난 달이면 내년으로
            if int(tmp_month) < thismonth :
                year = thisyear + 1
            month = tmp_month

            if tmp_day==None: # 일표현, 첫날 없는경우-> 마지막날
                tmp_day=calendar.monthrange(year,month)[1] # 달 마지막 일
            return [year,month,tmp_day]
        
        elif len(nextMonth)>0: # 다음달
            month = thismonth + 1
            if(month>12):
                month = month % 12
                year = thisyear + 1
            
            if tmp_day==None: # 일표현, 첫날 없는경우-> 마지막날
                tmp_day=calendar.monthrange(year,month)[1] # 달 마지막 일
            return [year,month,tmp_day]

        else: # 표시 없다면 오늘기준 지났으면 다음달, 아니면 이번달

            if tmp_day==None: # 일표현, 첫날 없는경우-> 마지막날
                tmp_day=calendar.monthrange(year,month)[1] # 달 마지막 일
            if tmp_day <= today :
                month = thismonth + 1
                if month > 12 :
                    month = month % 12
                    year = thisyear + 1
            day = tmp_day
            return [year,month,day]


    # 월 설정
    if len(searchMonth)>0: # 00월 
        tmp_month = searchMonth[len(searchMonth)-1][0:-1] #5월, 오월 - > 5, 오 , 십이 
        # 문자라면 숫자로 바꿔줌 일 이 삼 사 오 육(유) 칠 팔 구 십(시) 십일 십이
        if not (tmp_month>='1' and tmp_month<='9') :
            tmp_month = change_num(tmp_month)
        else: tmp_month = int(tmp_month)

        # 달 변경. 이미 지난 달이면 내년으로
        if int(tmp_month) < thismonth :
            year = thisyear + 1
        month = tmp_month
        
    elif len(nextMonth)>0: # 다음달
        month = thismonth + 1
        if(month>12):
            month = month % 12
            year = thisyear + 1
        
    # else default: 현재 달 

    # print(year,month,day)

    
        
    # 몇째 주 
    searchWeek = re.findall(r'마지막주|마지막 주|다음주|다음 주|다 다음주|다 다음 주|다다음 주|다다음주|[가-힣]{1,2}째주|[가-힣]{1,2}째 주|[0-9가-힣]{1,2}번째|[가-힣]{1,2} 번째',text)

    if len(searchWeek)>0:
        weektext = searchWeek[len(searchWeek)-1]
        # nextWeekFlag = False
        ## 주
        # 다음주, 다다음주, 넷째주 이런거 처리 -> 없으면 이번주로 판단
        # # -일이랑 요일이랑 day 변수 다르게해야될듯 ??
        if bool(re.search(r"다음주",weektext)) or bool(re.search(r"다음 주",weektext)):
            today_week = get_week_no(thisyear,thismonth,today) # 오늘이 몇째주인지
            year = thisyear
            month = thismonth
            
            if bool(re.search(r"다다음주",weektext)) or bool(re.search(r"다다음 주",weektext)) or bool(re.search(r"다 다음주",weektext)) or bool(re.search(r"다 다음 주",weektext)):
                week = today_week+2    
            else :
                week = today_week+1
            if(week>this_last_week):
                month = month+1
                if (bool(re.search(r"다다음주",weektext)) or bool(re.search(r"다다음 주",weektext))) and today_week==4:
                    print(week)
                    print(this_last_week)
                    print(today_week)
                    week = week - this_last_week+1
                else:
                    week = week- this_last_week
                if month > 12 :
                    month = month % 12
                    year = year + 1
        if bool(re.search(r"마지막주",weektext)) or bool(re.search(r"마지막 주",weektext)):
            tmp_last_day = calendar.monthrange(year,month)[1] # 이번 달 마지막 일
            week = get_week_no(year,month,tmp_last_day)
        else: # 몇째주, 몇번째주 이런거 
            tmp_week = None
            if bool(re.search(r"\D{1,2}째 주",weektext)):
                tmp_week = re.findall(r"\D{1,2}째 주",weektext)[0][0:-3] #넷째 주 -> 넷
                if(tmp_week=="첫"): week =1
                elif(tmp_week=="둘"): week=2
                elif(tmp_week=="셋"): week=3
                elif(tmp_week=="넷"): week=4
                elif(tmp_week=="다섯"): week=5
            elif bool(re.search(r"\D{1,2}째주",weektext)):
                tmp_week = re.findall(r"\D{1,2}째주",weektext)[0][0:-2] #넷째 주 -> 넷
                if(tmp_week=="첫"): week =1
                elif(tmp_week=="둘"): week=2
                elif(tmp_week=="셋"): week=3
                elif(tmp_week=="넷"): week=4
                elif(tmp_week=="다섯"): week=5
            elif bool(re.search(r"\w{1}번째",weektext)):
                tmp_week = re.findall(r"\w{1}번째",weektext)[0][0:-2] # 3번째 -> 3
                if(tmp_week=="첫"): week =1
                elif(tmp_week=="두"): week=2
                elif(tmp_week=="세"): week=3
                elif(tmp_week=="네"): week=4
                elif(tmp_week=="다섯"): week=5    
                else: week = int(tmp_week)
            elif bool(re.search(r"\D{1,2} 번째",weektext)):
                tmp_week = re.findall(r"\D{1,2} 번째",weektext)[0][0:-3] #네 번째 -> 네
                if(tmp_week=="첫"): week =1
                elif(tmp_week=="두"): week=2
                elif(tmp_week=="세"): week=3
                elif(tmp_week=="네"): week=4
                elif(tmp_week=="다섯"): week=5 
                else: week = int(tmp_week)
        if week==None:
            week = get_week_no(thisyear,thismonth,today) # 오늘이 몇째주인지
        tmp_idx=0
        if bool(re.search(r"\D{1}요일",text)):
            tmp_wday = re.findall(r"\D{1}요일",text)[-1][0:-2] 
            tmp_idx = ('월화수목금토일'.index(tmp_wday)) # 입력받은 값 월~일 인덱스
        tmp_day_list = get_day_from_weekday(year,month,week,int(tmp_idx))
        if tmp_day_list[0]==0: # 첫째주 문제 없는경우
            tmp_day = tmp_day_list[1]
            if(tmp_day > this_last_day): # 달 넘어간다면
                tmp_day = tmp_day - this_last_day
                month = month + 1
                if month > 12 :
                    month = month % 12
                    year = year + 1
            day = tmp_day
        else : #첫째주엥서 문제생기는경우 (달을 이전달로 해주거나 처리해주어야함)
            tmp_day = tmp_day_list[1]
            lastday_premonth=31
            if int(month)==1:
                lastday_premonth = calendar.monthrange(year-1,12)[1]
            else:
                lastday_premonth = calendar.monthrange(year,int(month)-1)[1]
            if tmp_day<=lastday_premonth: # 그 전달 마지막주가 첫째주에 포함되는경우
                day = tmp_day
                month = int(month)-1
            else : 
                day= tmp_day - lastday_premonth   
            tmp_last_day = calendar.monthrange(year,month)[1] # 이번 달 마지막 일
            if(day > tmp_last_day): # 달 넘어간다면
                day = day - tmp_last_day
                month = month + 1
                if month > 12 :
                    month = month % 12
                    year = year + 1   
        return [year,month,day]
            
        


    # 요일 -> 이번주 기준
    weekDay = re.findall(r"\D{1}요일",text)
    if len(weekDay)>0:
        tmp_wday = weekDay[-1][0:-2]
        tmp_idx = '월화수목금토일'.index(tmp_wday) # 입력받은 값 월~일 인덱스
        to_idx = calendar.weekday(thisyear,thismonth,today) # 오늘의 월~일 인덱스

        last_day= calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일

        if tmp_idx <= to_idx: # 이미 지난 요일 -> 다음주로 넘김
                day = today + 7-to_idx+tmp_idx
                if day > last_day :
                    day = day - last_day
                    month = month+1
                    if month > 12 :
                        month = month % 12
                        year = year + 1
        else :
            day = today + tmp_idx - to_idx
            if day > last_day :
                day = day - last_day
                month = month+1
                if month > 12 :
                    month = month % 12
                    year = year + 1
        return[year,month,day]


    return [year,month,day]
    # print(startEndDay, nextMonth, searchMonth,searchDay,weekDay,searchWeek)

