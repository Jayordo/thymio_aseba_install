import cv2
import climage

vid = cv2.VideoCapture(0)
ret, frame = vid.read()
cv2.imwrite('/tmp/frame.png', frame)
output = climage.convert('/tmp/frame.png')
print(output)
