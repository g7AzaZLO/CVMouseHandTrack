import cv2
import mouse
import numpy as np
import time


def LCM(img, x1, y1, length):
    cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
    mouse.click('left')



def RCM(img, x1, y1, length):
    cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
    mouse.click(button='right')


def chngVol(length, minVol, maxVol, volume):
    vol = np.interp(length, [-100, 180], [minVol, maxVol])
    volume.SetMasterVolumeLevel(vol, None)
