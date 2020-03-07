import cv2 as cv
import os
import numpy as np
from app.config import img_save

# Load Yolo (the model used for object detection)
net = cv.dnn.readNet('yolov3.weights', 'yolov3.cfg')
with open('yolov3.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
#Assuming less than 800 classes in an image
colors = np.random.uniform(0, 255, size=(800, 3))

def objdetect(img, ext):
    img = cv.cvtColor(np.array(img), cv.COLOR_BGR2RGB)
    height, width, channels = img.shape

    try:
        # Detecting objects
        blob = cv.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)
        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        indexes = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        font = cv.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[i]
                cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
                #Just to make sure that the label is visible for the corner cases
                if (y-30 > 0):
                    y_label_loc = y-5
                else:
                    y_label_loc = y + 20
                cv.putText(img, label, (x, y_label_loc), font, 1.5, color, 3)
                msg = ''
    except:
        msg = 'Failed to do object detection'
        img = img

    img_b = cv.imencode(('.'+ext), img)[1].tobytes()
    return img_b, height, width, msg
