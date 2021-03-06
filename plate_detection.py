# import required packages
import cv2
#from PIL import Image
#import pillow
#import pytesseract
import numpy as np

weight = "yolov3-custom_last.weights"
config = "yolov3-custom.cfg"


path = "40.jpeg"
image = cv2.imread("VEHICLE_IMAGE/"+path)
image = cv2.resize(image,(1020,1020))
Width = image.shape[1]
Height = image.shape[0]
scale = 0.00392

# read class names from text file
'''classes = None
with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]'''

classes = open("obj.names").read().strip().split("\n")

# generate different colors for different classes 
#COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# read pre-trained model and config file
net = cv2.dnn.readNet(weight, config)

# create input blob 
blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

# set input blob for the network
net.setInput(blob)


# function to get the output layer names 
# in the architecture
def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers

# function to draw bounding box on the detected object with class name
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h,i):
     
    label = str(classes[class_id])

    color = (100,255,100)
    #dummy variable
    y=y-5
    x=x-5
    cv2.rectangle(img, (x,y), (x_plus_w+5,y_plus_h), color, 2)
    print(x, y, x_plus_w, y_plus_h)
    img1 = image[y:y_plus_h,x:x_plus_w+5]
    cv2.putText(img, label, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    if(i==1): 
        cv2.imshow("imzg1",img1)
        cv2.imwrite("plate_output1/c"+path, img1)
        i=i+1
    else:
        cv2.imshow("imzg",img1)
        cv2.imwrite("plate_output1/"+path, img1)
    
    #pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    #text = pytesseract.image_to_string(img, lang="eng")
    #print(text)
# run inference through the network
# and gather predictions from output layers
outs = net.forward(get_output_layers(net))

# initialization
class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

# for each detetion from each output layer 
# get the confidence, class id, bounding box params
# and ignore weak detections (confidence < 0.5)
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x = int(detection[0] * Width)
            center_y = int(detection[1] * Height)
            w = int(detection[2] * Width)
            h = int(detection[3] * Height)
            x = center_x - w / 2
            y = center_y - h / 2
            class_ids.append(class_id)
            confidences.append(float(confidence))
            boxes.append([x, y, w, h])


# apply non-max suppression
indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

# go through the detections remaining
# after nms and draw bounding box
for i in indices:
    i = i[0]
    print(i)
    box = boxes[i]
    x = box[0]
    y = box[1]
    w = box[2]
    h = box[3]
    #print(x,y,w,h)
   
    draw_bounding_box(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h),i)

# display output image    
cv2.imshow("image", image)

# wait until any key is pressed
cv2.waitKey()
    
 # save output image to disk
cv2.imwrite("object-detection.jpg", image)


# release resources
cv2.destroyAllWindows()
