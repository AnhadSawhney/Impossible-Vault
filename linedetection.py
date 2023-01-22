import cv2 as cv
import numpy as np
import threading

# returns True if line is broken
def is_line_broken(vid): 
    print("Num lines detected:", vid.lines_detected)
    return vid.lines_detected != 1

# create a new thread that runs image capture/analysis
class CameraT(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.vid = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.img = None
        self.lines_detected = 1

    def run(self):
        ret,img = self.vid.read() # return a single frame in variable `img`
        self.img = cv.blur(img, (5,5))
        self.process_img(self, self.img)

    def process_img(self, img):

        #convert the BGR image to HSV colour space
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        # For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255]
        #set the lower and upper bounds for the green hue
        #limetape_rgb = (80, 255, 213)
        lower_green = np.array([18, 125, 110], np.uint8) # #rgb(160,183,0) = hsv(34, 266, 185)
        upper_green = np.array([45, 255, 255], np.uint8) ##rgb(204,242,1) = hsv(35, 255, 255)

        lower_white = np.array([30, 10, 235], np.uint8) # rgb(250, 250, 240) = hsv(0, 0, 245)
        upper_white = np.array([70, 250, 255], np.uint8) # rgb(255, 255, 255) = hsv(40, 0, 255)

        #create a mask for green colour using inRange function
        mask1 = cv.inRange(hsv, lower_green, upper_green)
        mask2 = cv.inRange(hsv, lower_white, upper_white)
        mask = cv.bitwise_or(mask1, mask2)

        #display the images
        #cv.imshow("mask1", mask1)
        #cv.imshow("mask2", mask2)
        #cv.imshow('mask combined', mask)

        contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contourAreas = [cv.contourArea(c) for c in contours] # area of contours
        self.lines_detected = len([area for area in contourAreas if area > 1000]) # 1000 being the min area of a detected line chunk to be considered a line (to ignore noise)
        print('Number of contours:', len(contours), "|", contourAreas)
        print('# tape lines:', self.lines_detected)
        if self.lines_detected != 1:
            print("line broken!")
        #print(contours)

        #cv.drawContours(img, contours, -1, (0,255,0), 3)
        #cv.imwrite("lines_mod.png", np.copy(img)) # see what was classified

        cv.waitKey(0)
        cv.destroyAllWindows()

#streamthread = StreamT(25)
#streamthread.start()


### orig script (now in class above)
'''
# define a video capture object
vid = cv.VideoCapture(0, cv.CAP_DSHOW)
ret,img = vid.read() # return a single frame in variable `img`
img = cv.blur(img, (5,5))
#cv.imshow('cam capture', img)


#convert the BGR image to HSV colour space
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

#set the lower and upper bounds for the green hue
#limetape_rgb = (80, 255, 213)

# For HSV, Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255]
lower_green = np.array([18, 125, 110], np.uint8) # #rgb(160,183,0) # hsv(34, 266, 185)
upper_green = np.array([45, 255, 255], np.uint8) ##rgb(204,242,1)# hsv(35, 255, 255)

lower_white = np.array([30, 10, 235], np.uint8) # rgb(250, 250, 240), hsv(0, 0, 245)
upper_white = np.array([70, 250, 255], np.uint8) # rgb(255, 255, 255), hsv(40, 0, 255)

#create a mask for green colour using inRange function
mask1 = cv.inRange(hsv, lower_green, upper_green)
mask2 = cv.inRange(hsv, lower_white, upper_white)
mask = cv.bitwise_or(mask1, mask2)
#perform bitwise and on the original image arrays using the mask
#res = cv.bitwise_and(img, img, mask=mask1)

#display the images
cv.imshow("mask1", mask1)
cv.imshow("mask2", mask2)
cv.imshow('mask combined', mask)
#cv.imshow("hsv", hsv)
#cv.imshow("res", res)

contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contourAreas = [cv.contourArea(c) for c in contours]
num_tape_lines = len([area for area in contourAreas if area > 1000]) # 1000 being the min area of a detected line chunk to be considered a line (to ignore noise)
print('Number of contours:', len(contours), "|", contourAreas)
print('# tape lines:', num_tape_lines)
if num_tape_lines != 1:
    print("line broken!")
#print(contours)

cv.drawContours(img, contours, -1, (0,255,0), 3)
cv.imwrite("lines_mod.png", np.copy(img)) # see what was classified

cv.waitKey(0)
cv.destroyAllWindows()
'''