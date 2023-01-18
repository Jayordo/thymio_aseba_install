import cv2
import climage

vid = cv2.VideoCapture(0)
while True:
    # Capture the video frame by frame
    ret, frame = vid.read()
    # function to resize
    # frame = cv2.resize(frame, (700, 500))

    # Display the resulting frame
    cv2.imwrite('/tmp/frame.png', frame)
    output = climage.convert('/tmp/frame.png')
    print(output)
    # the 'q' button is set as the quitting button you may use any desired button of your choice
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break
# After the loop release the cap object
vid.release()
