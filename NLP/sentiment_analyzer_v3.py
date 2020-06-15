from konlpy.tag import Komoran
from konlpy.tag import Kkma
import pandas as pd

class SentimentAnalyzer:

    def __init__(self, usejk):
        self.kkma = Kkma()

        pos_dict = pd.read_csv("/home/ec2-user/model/pos_dict_v3_kkma.csv")
        neg_dict = pd.read_csv("/home/ec2-user/model/neg_dict_v3_kkma.csv")
        pos_ans_csv = pd.read_csv("/home/ec2-user/model/pos_answer_dict_kkma.csv")
        neg_ans_csv = pd.read_csv("/home/ec2-user/model/neg_answer_dict_kkma.csv")

        self.pos_dict_1 = pos_dict[pos_dict['n-gram'] == 1]['word'].values.tolist()
        self.pos_dict_2 = pos_dict[pos_dict['n-gram'] == 2]['word'].values.tolist()
        self.pos_dict_3 = pos_dict[pos_dict['n-gram'] == 3]['word'].values.tolist()
        self.pos_dict_4 = pos_dict[pos_dict['n-gram'] == 4]['word'].values.tolist()

        self.neg_dict_1 = neg_dict[neg_dict['n-gram'] == 1]['word'].values.tolist()
        self.neg_dict_2 = neg_dict[neg_dict['n-gram'] == 2]['word'].values.tolist()
        self.neg_dict_3 = neg_dict[neg_dict['n-gram'] == 3]['word'].values.tolist()
        self.neg_dict_4 = neg_dict[neg_dict['n-gram'] == 4]['word'].values.tolist()


        self.pos_ans_dict = pos_ans_csv['ans'].values.tolist()
        self.neg_ans_dict = neg_ans_csv['ans'].values.tolist()

        self.use_jk = usejk

   
    def list_to_string(self, morphs_list):
        return ';'.join("%s/%s" % tup for tup in morphs_list)

    def list_to_string_without_jk(self, morphs_list):
        ret = ""
        for tup in morphs_list:
            if tup[1][:2] != "JK":
                ret = ret + ("%s/%s;" % tup)
        return ret

    # "문자열" -> "형태소/형태소;형태소/형태소"
    def pos_tagging(self, text):
        #morphs_list = self.komoran.pos(text)
        morphs_list = self.kkma.pos(text)
        if self.use_jk:
            return self.list_to_string(morphs_list)
        return self.list_to_string_without_jk(morphs_list)

    # pos_tagging 한 데이터를 입력
    # 긍정 단어, 부정 단어 리턴
    def count_word(self, text):
        pos_word = []
        neg_word = []

        for f in self.pos_dict_4:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                pos_word.append((f, idx))
                idx = text.find(f)

        for f in self.neg_dict_4:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                neg_word.append((f, idx))
                idx = text.find(f)

        for f in self.pos_dict_3:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                pos_word.append((f, idx))
                idx = text.find(f)

        for f in self.neg_dict_3:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                neg_word.append((f, idx))
                idx = text.find(f)

        for f in self.pos_dict_2:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                pos_word.append((f, idx))
                idx = text.find(f)

        for f in self.neg_dict_2:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                neg_word.append((f, idx))
                idx = text.find(f)

        for f in self.pos_dict_1:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                pos_word.append((f, idx))
                idx = text.find(f)

        for f in self.neg_dict_1:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                neg_word.append((f, idx))
                idx = text.find(f)

        return pos_word, neg_word
        
    def count_answer(self, text):
        pos_word = []
        neg_word = []


        for f in self.neg_ans_dict:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                neg_word.append(f)
                idx = text.find(f)

        for f in self.pos_ans_dict:
            idx = text.find(f)
            while idx != -1:
                text = text[:idx] + text[idx+len(f):]
                pos_word.append(f)
                idx = text.find(f)

        return len(pos_word), len(neg_word)

    def score_with_word(self, date_list, tagged_text):
        ret = []
        pos_cnt, neg_cnt = self.neg_rule(tagged_text)
        score = 0.0
        if pos_cnt != 0 or neg_cnt != 0:
            score = (pos_cnt - neg_cnt)/(pos_cnt + neg_cnt)
        
        for dt in date_list:
            ret.append((dt[0], score))

        return ret

    def score_with_answer(self, date_list, tagged_text, is_prev_q):
        ret = []
        if not is_prev_q:
            return self.score_with_word(date_list, tagged_text)

        pos_cnt, neg_cnt = self.count_answer(tagged_text)
        if pos_cnt == 0 and neg_cnt == 0:
            return self.score_with_word(date_list, tagged_text)

        else:
            score = 0
            if (pos_cnt - neg_cnt) > 0:
                score = 1
            else:
                score = -1

            for dt in date_list:
                ret.append((dt[0], dt[1] * score))

            return ret

    def sentiment_analysis(self, date_list, text, is_prev_q):
        ret = []
        tagged = self.pos_tagging(text)
        
        return self.score_with_answer(date_list, tagged, is_prev_q)

    def find_neg(self, text, start_idx, end_idx):
        neg_pre = ['안/MAG;', '못/MAG;', '밖에/JX;', '아니/VV;면/ECE;', '말/VV;고/ECE;', '말/VV;고는/ECE;']
        neg_post = [';지/ECD;못', ';지/ECD;않/VXV', ';지/ECD;말/VXV', ';지/ECD;는/JX;못', ';지/ECD;는/JX;않/VXV', ';지/EFN;는/JX;말/VXV', ';지/EFN;는/JX;못', ';지/EFN;는/JX;않/VXV', ';지/EFN;는/JX;말/VXV']

        st = start_idx
        ed = end_idx

        inv = False

        for i in neg_pre:
            if text[start_idx - len(i):start_idx] == i:
                st = start_idx - len(i)
                inv = not inv
        
        for i in neg_post:
            if text[end_idx:end_idx + len(i)] == i:
                ed = end_idx + len(i)
                inv = not inv

               
        return inv



    def neg_rule(self, text):
        pos_word, neg_word = self.count_word(text)
        pos_list = []
        neg_list = []
        for i in pos_word:
            if self.find_neg(text, i[1], i[1] + len(i[0])):
                neg_list.append(i)
            else:
                pos_list.append(i)

        for i in neg_word:
            if self.find_neg(text, i[1], i[1] + len(i[0])):
                pos_list.append(i)
            else:
                neg_list.append(i)

        return len(pos_list), len(neg_list)
            

