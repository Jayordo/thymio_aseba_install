#the camera integration and processing
import cv2


def take_picture():
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    vid.release()
    return ret, frame


def pre_process_image(image):
    # do some numpy processing(filter colours, resizing image, etc)
    pass


def process_image(image_matrix, model):
    # use some (pre-trained) model to convert image to interpretable 'memory'
    pass
