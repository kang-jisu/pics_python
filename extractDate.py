
#-*- coding:utf-8 -*-
import urllib3
import json
import calendar
import re
import math

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
    

def get_week_no(y, m, d):
  firstday = calendar.weekday(y,m,1) # 첫날의 월~일 인덱스
  if firstday == 6: # 일요일
    origin = 1
  elif firstday < 3: # 월,화,수
    origin = 1-(3-firstday)
  else: # 목,금,토 -> 다음주 일요일이 첫째주 기준
    origin = 1 + 6-firstday
  return math.floor((d-origin)/7 + 1)

def get_day_from_weekday(y, m, week,day):
    firstday = calendar.weekday(int(y),int(m),int(1)) # 첫날의 월~일 인덱스 0 : 월 6 : 일
    if firstday == 6: # 일요일
        origin = 1
        return [0,origin+ (week-1)*7 + day]
    elif firstday < 3: # 월,화,수
        lastday_premonth = 31
        if m==1:
            lastday_premonth = calendar.monthrange(y-1,12)[1]
        else:
            lastday_premonth = calendar.monthrange(y,int(m)-1)[1]
        lastday_premonth = lastday_premonth-firstday  # 전 달의 마지막 일요일 
        # print(y,"년",m,"월",week,"째 주",day,"요일")
        result = lastday_premonth + (week-1)*7+day
        return [-1,result]
    else: # 목,금,토 -> 다음주 일요일이 첫째주 기준
        origin = 1 + 6-firstday
        return [0,origin+ (week-1)*7 + day]


result = {"text":None,}

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

thisyear= startDate.tm_year
thismonth= startDate.tm_mon
today = startDate.tm_mday
# today = 28
this_last_day = calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일
this_last_week = get_week_no(thisyear,thismonth,this_last_day)

year = startDate.tm_year
month = startDate.tm_mon
#month = 12
day = startDate.tm_mday
week = None 


year_flag = False
month_flag = False
day_flag = False
week_flag = False


special_day = ["신정","삼일절","어린이날","어린이 날","근로자의 날","근로자의날","어버이날","어버이 날","스승의날","스승의 날","현충일","제헌절","광복절","개천절","한글날","크리스마스","성탄절","화이트데이","발렌타인데이","빼빼로데이"]
special_day_value = ["01 01","03 01","05 05","05 05","05 01","05 01","05 08","05 08","05 15","05 15","06 06","07 17","08 15","10 03","10 09","12 25","12 25","03 14","02 14","11 11"]


while(1):
    print("")
    text  = input()
    if(text=="끝"):
        break

    else:    
        # 기념일
        break_flag = False
        for i in range (len(special_day)):
            if bool(re.match(special_day[i],text)):
                date = special_day_value[i].split(" ")
                year = thisyear
                month = date[0]
                day = date[1]
                print(year,month,day)
                #다른건 다 올해 설날,추석, 신정만 내년 고려할것
                break_flag = True
        if break_flag ==True: break
        # 월 정보
        if bool(re.search(r"내일",text)):
            day = today + 1
            month = thismonth
            year = thisyear
            last_day= calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일
            if day > last_day :
                day = day - last_day
                month = thismonth+1
                if month > 12 :
                    month = month % 12
                    year = thisyear + 1  
            day_flag=True
            month_flag=True
            week_flag=True
            year_flag=True
            print(year, month, day)              

        if bool(re.search(r"모레",text)):
            day = today + 2
            month = thismonth
            year = thisyear
            last_day= calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일
            if day > last_day :
                day = day - last_day
                month = thismonth+1
                if month > 12 :
                    month = month % 12
                    year = thisyear + 1  
            day_flag=True
            month_flag=True
            week_flag=True
            year_flag=True
            print(year, month, day)
        

        # 다음 달
        if month_flag==False and (bool(re.search(r"다음 달",text)) or bool(re.search(r"다음달",text)) or bool(re.search(r"담달",text))):
            month = month + 1
            month_flag = True
            if(month>12):
                month = month % 12
                year = year + 1
        
            print(year, month, day)

        # -- 월
        if month_flag==False:
            if bool(re.search(r"\w{1,2}월",text)) :
                print(text)

                tmp_month = re.search(r"\w{1,2}월",text).string[0:-1] #5월, 오월 - > 5, 오 , 십이 
                # 문자라면 숫자로 바꿔줌 일 이 삼 사 오 육(유) 칠 팔 구 십(시) 십일 십이
                if not (tmp_month>='1' and tmp_month<='9') :
                    tmp_month = change_num(tmp_month)
                
                # 달 변경. 이미 지난 달이면 내년으로
                if int(tmp_month) < month :
                    year = year + 1
                month = tmp_month
                month_flag = True

                print(year, month, day)
        
        ## 일

        if bool(re.search(r"\w{1,3}일",text)) and not bool(re.search(r"요일",text)) and not bool(re.search(r"내일",text)):
            tmp_day = re.search(r"\w{1,3}일",text).string[0:-1] #5일, 십육일 - > 5, 십육 

            if bool(re.search(r"\d{1,3}",tmp_day)):
                tmp_day = int(tmp_day)
            else:
                tmp_day = change_num(tmp_day)

            print(tmp_day)

            if month_flag == False :
                if tmp_day <= today :
                    month = month + 1
                    if month > 12 :
                        month = month % 12
                        year = year + 1
                
            day = tmp_day
            day_flag=True
            week_flag=True
            print(year, month, day)

        ## 주
        # 다음주, 다다음주, 넷째주 이런거 처리 -> 없으면 이번주로 판단
        # # -일이랑 요일이랑 day 변수 다르게해야될듯 ??
        if week_flag==False and not bool(re.search(r"주말",text)) and (bool(re.search(r"주",text)) or bool(re.search(r"째",text))):
            if bool(re.search(r"다음주",text)) or bool(re.search(r"다음 주",text)):
                today_week = get_week_no(thisyear,thismonth,today) # 오늘이 몇째주인지
                
                if bool(re.search(r"다다음주",text)) or bool(re.search(r"다다음 주",text)):
                    week = today_week+2
                else :
                    week = today_week+1

                if(week>this_last_week):
                    month = thismonth+1
                    week = week - this_last_week
                    if month > 12 :
                        month = month % 12
                        year = year + 1
                week_flag=True
            elif bool(re.search(r"\D{1,2}째 주",text)) or bool(re.search(r"\D{1,2}째주",text)) or bool(re.search(r"\D{1,2} 번째",text)):

                tmp_week = None
                if bool(re.search(r"\D{1,2}째 주",text)):
                    tmp_week = re.findall(r"\D{1,2}째 주",text)[0][0:-3] #넷째 주 -> 넷
                    if(tmp_week=="첫"): week =1
                    elif(tmp_week=="둘"): week=2
                    elif(tmp_week=="셋"): week=3
                    elif(tmp_week=="넷"): week=4
                    elif(tmp_week=="다섯"): week=5
                elif bool(re.search(r"\D{1,2}째주",text)):
                    tmp_week = re.findall(r"\D{1,2}째주",text)[0][0:-2] #넷째 주 -> 넷
                    if(tmp_week=="첫"): week =1
                    elif(tmp_week=="둘"): week=2
                    elif(tmp_week=="셋"): week=3
                    elif(tmp_week=="넷"): week=4
                    elif(tmp_week=="다섯"): week=5
                else:
                    tmp_week = re.findall(r"\D{1,2} 번째",text)[0][0:-3] #네 번째 -> 네
                    if(tmp_week=="첫"): week =1
                    elif(tmp_week=="두"): week=2
                    elif(tmp_week=="세"): week=3
                    elif(tmp_week=="네"): week=4
                    elif(tmp_week=="다섯"): week=5
                week_flag=True
            elif bool(re.search(r"\w{1}번째",text)):
                tmp_week = re.findall(r"\w{1}번째",text)[0][0:-2] # 3번째 -> 3
                if(tmp_week=="첫"): week =1
                elif(tmp_week=="두"): week=2
                elif(tmp_week=="세"): week=3
                elif(tmp_week=="네"): week=4
                elif(tmp_week=="다섯"): week=5    
                else: week = tmp_week
                week_flag=True
            else :
                week = get_week_no(thisyear,thismonth,today) # 오늘이 몇째주인지
                week_flag=True

            if bool(re.search(r"\D{1}요일",text)):
                tmp_wday = re.findall(r"\D{1}요일",text)[0][0:-2] 
                tmp_idx = ('일월화수목금토'.index(tmp_wday)) # 입력받은 값 월~일 인덱스
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
                day_flag =True



        ## 요일 
        # 일단은 이번주 기준
        if day_flag==False and week_flag==False:
            if bool(re.search(r"\D{1}요일",text)):
                tmp_wday = re.findall(r"\D{1}요일",text)[0][0:-2] 
                tmp_idx = '월화수목금토일'.index(tmp_wday) # 입력받은 값 월~일 인덱스
                to_idx = calendar.weekday(thisyear,thismonth,today) # 오늘의 월~일 인덱스

                last_day= calendar.monthrange(thisyear,thismonth)[1] # 이번 달 마지막 일

                if tmp_idx <= to_idx: # 이미 지난 요일 -> 다음주로 넘김
                        print("다음주",tmp_wday,"요일")
                        day = today + 7-to_idx+tmp_idx
                        if day > last_day :
                            day = day - last_day
                            if month_flag==False:
                                month = month+1
                                if month > 12 :
                                    month = month % 12
                                    year = year + 1
                else :
                    print("이번주",tmp_wday,"요일")
                    day = today + tmp_idx - to_idx
                    if day > last_day :
                        day = day - last_day
                        if month_flag==False:  # 달 넘어가면 달 넘기고 해 넘어가면 해 넘김
                            month = month+1
                            if month > 12 :
                                month = month % 12
                                year = year + 1
                day_flag=True
                print(year, month, day)
                

            elif bool(re.search(r"첫날",text)) or bool(re.search(r"첫 날",text)):
                day = 1
                day_flag=True
                print(year, month, day)

            elif bool(re.search(r"마지막날",text))or bool(re.search(r"마지막 날",text)):
                last_day= calendar.monthrange(thisyear,month)[1] # 이번 달 마지막 일
                day = last_day
                day_flag=True
                print(year, month, day)


        else:
            
            print(year, month, day)            
        
        