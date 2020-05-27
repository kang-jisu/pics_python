from object_detection.speech_balloon_detect import SpeechBalloonDetector
from object_detection.ocr.OCR import TextDetection
import os

class ImageToText:
    def __init__(self):
        self.sd = SpeechBalloonDetector()
        self.td = TextDetection()
        self.CWD_PATH = os.getcwd()

    def image_to_text(self, path):
        img_path = os.path.join(self.CWD_PATH, path)
        # img_path = os.path.join(path)
        sentences = self.td.detect_document(img_path)
        boxes = self.sd.detect_boundings(img_path)

        sentences_in_image = []
        for bound, text in sentences:
            xmin = bound.vertices[0].x
            ymin = bound.vertices[0].y
            xmax = bound.vertices[3].x
            ymax = bound.vertices[3].y
            for box in boxes:
                b_ymin, b_xmin, b_ymax, b_xmax = box
                if b_ymin <= ymin and b_ymax >= ymax and b_xmin <= xmin and b_xmax >= xmax:
                    sentences_in_image.append(text)
                    break

        return sentences_in_image

            
            

