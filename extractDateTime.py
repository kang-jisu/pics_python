
def extractDateTIme(status,text):
    # status : "DATETIME","DATE","TIME"으로 구분

    if status=="DATETIME":
        #extractDate+time 따로 불러와서 실행하면됨
        print("datetime")
    elif status=="DATE":
        print("date")
    elif status=="TIME":
        #extracttime에서 오늘인지 내일인지 구분해줌
        print("time")

    return "2020 05 27"

# 날짜 예시
# 0월 00일 ( 가장 무난한 경우)
# 00일, 몇째주 무슨요일 ( 달 표시 없이 -> 이번달로), 다음주 무슨요일, 다다음주 무슨요일
# 다음달,0월 +  첫날, 마지막날, 00일, 몇째주 무슨요일
# 기념일
# 내일, 모레

# 몇시 몇분

# MAIN 함수

status = "DATETIME"
# status = "TIME"
# status = "DATE"
text = "2020년 5월 27일"

result = extractDateTIme(status,text)
print(result)

