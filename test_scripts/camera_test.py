import cv2
import climage
import select
import sys
import time

vid = cv2.VideoCapture(0)
while True:
    user_input = select.select([sys.stdin], [], [], 1)[0]
    if user_input:
        value = sys.stdin.readline().rstrip()
        if value == "q":
            print("Exiting")
            break
        else:
            print("You entered: %s" % value)
    else:
        ret, frame = vid.read()
        cv2.imwrite('/tmp/frame.png', frame)
        output = climage.convert('/tmp/frame.png', is_truecolor=False, width=150, palette="linuxconsole")
        print(output)
        #depending on machine not requiredq
        time.sleep(0.2)

vid.release()
