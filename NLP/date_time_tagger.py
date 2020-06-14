special_days = ["오늘","내일","모레","글피","신정","삼일절","어린이날","어린이 날","근로자의 날","근로자의날","어버이날","어버이 날","스승의날","스승의 날","현충일","제헌절","광복절","개천절","한글날","크리스마스","성탄절","화이트데이","발렌타인데이","빼빼로데이"]
days = '월화수목금토일'


def date_time_tagger(text, dt_type):
    if dt_type[:2] == 'DT':
        #기념일, 오늘, 내일, 모레, 글피
        if any(d in text for d in special_days):
            return 7
        #?요일
        elif '요일' in text:
            return 1
        #월화수목금토일
        elif text[0] in days:
            return 1
        #다음달, 이번달, ?월
        elif '달' in text or '월' in text:
            return 4
        elif '주' in text:
            #다음주, 이번주
            if '다음주' in text or '이번주' in text or '다다음주' in text:
                return 6
            #둘째주, ...
            else:
                return 2
        #?일
        elif '일' in text:
            idx = text.find('일')
            if idx < 1:
                return 0
            if text[idx-1] in "1234567890" or text[idx-1] in "일이삼사오육칠팔구십":
                return 2
            return 0
        else:
            return 0

    else:
        if '시' in text:
            return 8
        elif '분' in text or '반' in text or text.isdecimal():
            return 16
        elif '오전' in text or '오후' in text or '밤' in text or '낮' in text:
            return 32
        else:
            return 0


def dt_select(dt_list):
    #dt_list : [((금요일, DT_OTHERS), 1.0), ((),), ((), ), ...]

    dt_dict = {}
    order = 0
    for i in dt_list:
        dt_dict[i[0][0]] = (i[0][1], i[1], order)
        order += 1

    print('dt_dict')
    print(dt_dict)
    
    dt_list_sorted = []
    for key, val in dt_dict.items():
        dt_list_sorted.append((key, val[0], val[1], val[2]))
    
    #[(금요일, DT_OTHERS, 1.0), (), ()]
    dt_list_sorted.sort(key = lambda k : (k[2], k[3]), reverse=True)

    ret_DT = ""
    ret_TI = ""
    ret_bin = 0
    for i in dt_list_sorted:
        dt_tag = date_time_tagger(i[0], i[1])
        if ret_bin & dt_tag == 0:
            ret_bin = ret_bin | dt_tag
            if i[1][:2] == 'DT':
                ret_DT = ret_DT + ' ' + i[0]
            else:
                ret_TI = ret_TI + ' ' + i[0]

    return ret_DT, ret_TI
