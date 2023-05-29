import ttools.movement as tmo
from tdmclient import ClientAsync
import cv2


def object_rec(img):
    # Convert to graycsale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Blur the image for better edge detection
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    # Sobel Edge Detection
    # sobelx = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5)  # Sobel Edge Detection on the X axis
    # sobely = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5)  # Sobel Edge Detection on the Y axis
    # sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5)  # Combined X and Y Sobel Edge Detection
    # # Display Sobel Edge Detection Images
    # cv2.imshow('Sobel X', sobelx)
    # cv2.waitKey(0)
    # cv2.imshow('Sobel Y', sobely)
    # cv2.waitKey(0)
    # cv2.imshow('Sobel X Y using Sobel() function', sobelxy)
    # cv2.waitKey(0)
    # Canny Edge Detection
    edges = cv2.Canny(image=img_blur, threshold1=50, threshold2=200)  # Canny Edge Detection
    # Save Canny Edge Detection Image
    cv2.imwrite('tmp/edges.png', edges)


with ClientAsync() as client:
    vid = cv2.VideoCapture(0)


    async def basic_loop():
        runtime = 0
        max_runtime = 1
        with await client.lock() as node:
            while runtime <= max_runtime:
                ret, frame = vid.read()
                object_rec(frame)
                await client.sleep(0.1)
                runtime += 1
            await node.set_variables(tmo.generate_motor_targets(0, 0))


    client.run_async_program(basic_loop)
    vid.release()
