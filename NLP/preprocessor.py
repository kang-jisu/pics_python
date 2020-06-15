def preprocess(text):
    for idx in range(len(text)):
        line = text[idx]
        
        line = line.replace('다 다음 주', '다다음주')
        line = line.replace('다음 주', '다음주')
        line = line.replace('이번 주', '이번주')
        line = line.replace('째 주', '째주')
        line = line.replace('이번 달', '이번달')
        line = line.replace('다음 달', '다음달')
        line = line.replace('오후 ', '오후')
        line = line.replace('오전 ', '오전')
        line = line.replace('시 반', '시반')
        
        text[idx] = line

    return text
