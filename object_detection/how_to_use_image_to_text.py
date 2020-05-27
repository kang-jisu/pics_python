from image_to_text import ImageToText

itt = ImageToText()
image_name = 'test4.jpg'    #이부분 cwd+파일명으로 구현되어 있는데 절대경로가 나으면 수정할 수 있습니다!

#문장 가져오기!
sentences = itt.image_to_text(image_name)
print(sentences)