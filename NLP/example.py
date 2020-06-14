"""
실행 전 수정해야 하는 부분
1. sentiment_analyzer_v3 의 PATH_ 4개
2. intent_analyzer의 PATH_ 2개
3. datetime_recognizer의 ACCESSKEY
"""

from entity_sentiment_v4 import DateTimeSentimentAnalyzer
from date_time_tagger import dt_select

dtsa = DateTimeSentimentAnalyzer(False)
texts = ['월요일에 만나요!', '좋습니다']
result = dt_select(dtsa.entity_sentiment_analyzer(texts))
print(result)