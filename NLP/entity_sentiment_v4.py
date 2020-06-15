#-*- coding:utf-8 -*-

from konlpy.tag import Kkma

import urllib3
import json

from NLP.sentiment_analyzer_v3 import SentimentAnalyzer
from NLP.datetime_recognizer import datetime_recognizer

from NLP.intent_analyzer import IntentAnalyzer
from NLP.preprocessor import preprocess


class DateTimeSentimentAnalyzer:
    def __init__(self, usejk=True):
        self.sent_analyzer = SentimentAnalyzer(usejk)
        self.result = []
        self.kkma = Kkma()
        self.ia = IntentAnalyzer()
        
    def split_sentence_with_ec(self, text):
        ret = []
        string = ""
        words = text.split()
        for idx in range(len(words)):
            i = words[idx]
            pos = self.kkma.pos(i)
            string = string + i + ' '

            #다음 단어가 특수기호면 넘어감
            if idx != len(words) - 1:
                next_word = self.kkma.pos(words[idx + 1])
                if next_word[-1][1][0] == "S":
                    continue

            if pos[len(pos)-1][1][:2] == "ECE":
                ret.append(string)
                string = ""
            elif pos[len(pos)-1][1][:2] == "IC":
                ret.append(string)
                string = ""
            elif pos[len(pos)-1][1][0] == "S":
                ret.append(string)
                string = ""
            
        if len(string) != 0:
            ret.append(string)
        
        for i in range(len(ret)):
            if not ret[i]:
                continue
            while ret[i][-1] == ' ':
                ret[i] = ret[i][:-1]

        return ret

    def split_sentence_with_s(self, text):
        #text : list of str
        clustered_texts = []
        ct = []
        s = ",;:\\^.\'\"~!()<>[]?"
        for i in text:
            clustered_texts = []
            tmp_text = i
            for ch_idx in range(len(i) - 2, -1, -1):
                if i[ch_idx] in s and i[ch_idx + 1] not in s:
                    clustered_texts.insert(0,tmp_text[ch_idx + 1:])
                    tmp_text = tmp_text[:ch_idx + 1]
                    if ch_idx == 0:
                        clustered_texts.insert(0,tmp_text)
                elif ch_idx == 0:
                    clustered_texts.insert(0, tmp_text)
                
            ct.extend(clustered_texts)

        return ct

    def entity_sentiment_analyze(self, sentences):
        #sentences : list of str
        result = []
        dt_before = []
        is_prev_q = False
        sentences = self.split_sentence_with_s(sentences)
        sentences = preprocess(sentences)
        for i in sentences:
            is_q = self.ia.is_question(i)
            has_dt = len(datetime_recognizer(i))
            text = self.split_sentence_with_ec(i)

            if has_dt != 0 and is_q:
                if result and dt_before:
                    if result[-1][0] == dt_before[-1][0]:
                        dt_before = []
                prev_dt = []
                for j in text:
                    new_dt = False
                    dt_list = datetime_recognizer(j)
                    if len(dt_list) != 0:
                        for k in range(len(dt_list)):
                            dt_list[k] = (dt_list[k], 0.0)
                        prev_dt += dt_list
                        new_dt = True
                    else:
                        dt_list = prev_dt
                    sent_result = self.sent_analyzer.sentiment_analysis(dt_list, j, is_prev_q)
                    if new_dt:
                        dt_before = dt_before + sent_result
                    else:
                        for sr in sent_result:
                            if sr[1] != 0:
                                dt_before.append(sr)


            elif has_dt != 0 and not is_q:
                if result and dt_before:
                    if result[-1][0] == dt_before[-1][0]:
                        dt_before = []
                    else:
                        result.extend(dt_before)
                        dt_before = []
                elif not result and dt_before:
                    result.extend(dt_before)
                    dt_before = []
                prev_dt = []
                for j in text:
                    new_dt = False
                    dt_list = datetime_recognizer(j)
                    if len(dt_list) != 0:
                        for k in range(len(dt_list)):
                            dt_list[k] = (dt_list[k], 0.0)
                        prev_dt += dt_list
                        new_dt = True
                    else:
                        dt_list = prev_dt
                    sent_result = self.sent_analyzer.sentiment_analysis(dt_list, j, is_prev_q)
                    if new_dt:
                        dt_before = dt_before + sent_result
                    else:
                        for sr in sent_result:
                            if sr[1] != 0:
                                dt_before.append(sr)

                result.extend(dt_before)

            elif has_dt == 0 and is_q:
                if not dt_before:
                    continue
                dt_before = self.sent_analyzer.sentiment_analysis(dt_before, i, is_prev_q)

            else:
                if not dt_before:
                    continue
                
                sent_ret = self.sent_analyzer.sentiment_analysis(dt_before, i, is_prev_q)
                sent_add = []
                if result:
                    for dt in sent_ret:
                        if dt[1] != 0:
                            sent_add.append(dt)
                else:
                    sent_add = sent_ret

                result.extend(sent_add)

            is_prev_q = is_q


        if dt_before:
            if not result:
                result.extend(dt_before)
            elif result[-1][0] != dt_before[-1][0]:
                result.extend(dt_before)

        return result
