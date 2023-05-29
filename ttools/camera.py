#the camera integration and processing
import cv2

# TODO: readup on how to create/run model
# https://www.tensorflow.org/lite/guide/inference#load_and_run_a_model_in_python
# https://www.tensorflow.org/api_docs/python/tf/lite/Interpreter
import tflite_runtime.interpreter as tflite

def take_picture():
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    vid.release()
    return frame


def pre_process_image(image):
    # do some numpy processing(filter colours, resizing image, etc)
    pass


def process_image(image_matrix, model):
    # here's an example cnn model
    # https://www.geeksforgeeks.org/convolutional-neural-network-cnn-in-tensorflow/
    # TODO: find example convolution kernels to use

    # from tensorflow.keras.models import Sequential
    # from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
    #
    # model = Sequential()
    #
    # # Layer 1
    # # Conv 1
    # model.add(Conv2D(filters=6, kernel_size=(5, 5), strides=1, activation='relu', input_shape=(32, 32, 1)))
    # # Pooling 1
    # model.add(MaxPooling2D(pool_size=(2, 2), strides=2))
    #
    # # Layer 2
    # # Conv 2
    # model.add(Conv2D(filters=16, kernel_size=(5, 5), strides=1, activation='relu'))
    # # Pooling 2
    # model.add(MaxPooling2D(pool_size=2, strides=2))
    #
    # # Flatten
    # model.add(Flatten())

    #here be dense layers if needed
    pass
