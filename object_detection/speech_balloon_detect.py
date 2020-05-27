# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

# Import utilites

class SpeechBalloonDetector:
    def __init__(self):
                
        # This is needed since the notebook is stored in the object_detection folder.
        sys.path.append("..")
        from object_detection.utils import label_map_util    
        from object_detection.utils import visualization_utils as vis_util
        import object_detection.select_bounding_boxes as sb_util

        # Name of the directory containing the object detection module we're using
        self.MODEL_NAME = 'inference_graph'

        # Grab path to current working directory
        self.CWD_PATH = os.getcwd()

        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection.
        PATH_TO_CKPT = os.path.join(self.CWD_PATH, self.MODEL_NAME,'frozen_inference_graph.pb')

        # Path to label map file
        PATH_TO_LABELS = os.path.join(self.CWD_PATH,'training','object-detection.pbtxt')


        # Number of classes the object detector can identify
        NUM_CLASSES = 1

        # Load the label map.
        # Label maps map indices to category names, so that when our convolution
        # network predicts `5`, we know that this corresponds to `king`.
        # Here we use internal utility functions, but anything that returns a
        # dictionary mapping integers to appropriate string labels would be fine
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # Load the Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=self.detection_graph)

    def detect_boundings(self, path):
        sys.path.append("..")
        from object_detection.utils import label_map_util    
        from object_detection.utils import visualization_utils as vis_util
        import object_detection.select_bounding_boxes as sb_util
        
        #IMAGE_NAME = path
        # Path to image
        #PATH_TO_IMAGE = os.path.join(self.CWD_PATH,IMAGE_NAME)
        PATH_TO_IMAGE = path
        
        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Load image using OpenCV and
        # expand image dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        image = cv2.imread(PATH_TO_IMAGE)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_expanded = np.expand_dims(image_rgb, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = self.sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        #print('boxes : ')
        #print(np.shape(boxes))

        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)

        boxes_selected = sb_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)

        #print(boxes_selected)
        return boxes_selected

        """

        ############
        #resize image
        #image = cv2.resize(image, dsize=(360,740))


        # All the results have been drawn on image. Now display the image.
        #cv2.imshow('Object detector', image)

        # Press any key to close the image
        #cv2.waitKey(0)

        cv2.imwrite('result4.jpg', image)

        # Clean up
        cv2.destroyAllWindows()
        """