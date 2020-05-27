from google.cloud import vision
import io

class TextDetection:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def detect_text(self, path):
        """Detects text in the file."""

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
