import cv2 as cv
import numpy as np
import threading
import pygame.image
import time

# create a new thread that runs image capture/analysis
class CameraT(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.vid = cv.VideoCapture(-1)
        self.img = None
        self.imgout = None
        self.lines_detected = 1
        self.event = event

    #def terminate(self):
    #    self.event.set()

    def run(self):
        while not self.event.is_set():
            ret,img = self.vid.read() # return a single frame in variable `img`
            self.imgout = img
            self.img = cv.blur(img, (5,5))
            self.process_img(self.img)
            self.event.wait(0.1)

        cv.waitKey(0)
        cv.destroyAllWindows()

    def c2ImageToSurface(cvImage):
        if cvImage.dtype.name == 'uint16':
            cvImage = (cvImage / 256).astype('uint8')
        size = cvImage.shape[1::-1]
        if len(cvImage.shape) == 2:
            cvImage = np.repeat(cvImage.reshape(size[1], size[0], 1), 3, axis = 2)
            format = 'RGB'
        else:
            format = 'RGBA' if cvImage.shape[2] == 4 else 'RGB'
            cvImage[:, :, [0, 2]] = cvImage[:, :, [2, 0]]
        surface = pygame.image.frombuffer(cvImage.flatten(), size, format)
        return surface.convert_alpha() if format == 'RGBA' else surface.convert()

    def getImageForPygame(self):
        if self.imgout is None:
            return None
        return CameraT.c2ImageToSurface(self.imgout)

    # returns True if line is broken
    def is_line_broken(self): 
        print("Num lines detected:", self.lines_detected)
        return self.lines_detected != 1

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
        self.imgout = mask

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

#streamthread = StreamT(25)
#streamthread.start()