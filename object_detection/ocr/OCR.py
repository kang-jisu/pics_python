from google.cloud import vision
import io

import argparse
from enum import Enum
#import io
#from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw


class TextDetection:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    """
    def detect_text(self, path):
        #Detects text in the file.
        
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        print('Texts:')
        
        bounds = []

        for text in texts:
            print('\n"{}"'.format(text.description))

            #vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])

            #print('bounds: {}'.format(','.join(vertices)))
            
            bounds.append(text.bounding_poly)

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
            
        return bounds, texts
    
    def detect_document(self, path):
        #Detects document features in an image.

        # [START vision_python_migration_document_text_detection]
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = self.client.document_text_detection(image=image)

        sentences = []
        word_list = []
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        word_list.append(word_text)
                    sentence = ' '.join([w for w in word_list])
                    sentences.append(tuple((paragraph.bounding_box, sentence)))
                    word_list = []


        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        return sentences
    """

    def detect_document(self, path):
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = self.client.document_text_detection(image=image)
        texts = response.text_annotations
        entire_text = texts[0].description.replace('\n', ' ')    
        
        sentences = []
        word_list = []
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        word_list.append(word_text)
                    sentence = ''.join([w for w in word_list])
                    sentences.append(tuple((paragraph.bounding_box, sentence)))
                    word_list = []
                    
        idx = 0
        prev = 0
        result = []
        
        for bound, text in sentences:
            sz = 0
            while sz < len(text):
                if entire_text[idx] != ' ':
                    sz += 1
                idx += 1
            
            idx += 1     
            result.append((bound, entire_text[prev:idx].strip()))
            prev = idx


        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        return result
