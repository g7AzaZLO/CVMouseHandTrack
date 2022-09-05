# Program by ZLO#DEV
# Original link on project https://github.com/MaloyMeee/CVMouseHandTrack


import cv2
import mediapipe as mp
import pyautogui as pag
import mouse
import numpy as np
import time
import HandTrackingModule as htm
import CVfunc as func
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


def main():
    # Camera ###########
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    wCam, hCam = 640, 480
    cam.set(3, wCam)
    cam.set(4, hCam)
    ####################

    # FPS ##############
    pTime = 0
    ####################

    # Detector #########
    detector = htm.handDetector(maxHands=1)
    ####################

    # Screen size ######
    wScr, hScr = pag.size()
    # print(wScr, hScr) # screen size output
    frameR = 150  # reducing the input window
    ####################

    # Smoothing the mouse
    smooth = 3
    plocX, plocY = 0, 0
    clockX, clockY = 0, 0
    ####################

    # Volume ###########

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    print(volRange)
    minVol = volRange[0]
    maxVol = volRange[1]
    ####################

    # experemental distance
    # x = [270, 220, 184, 159, 137, 121, 111, 98, 91, 82, 78, 71, 70, 44, 61, 57, 54, 52, 50]
    # y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110]
    #####################

    # Flag ##############

    flag = False
    #####################
    while True:
        success, img = cam.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        # We track the position of the index
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]

        # Check which hand
        whathnd = detector.whatHand()
        # Check whether the finger is raised
        finup = detector.fingersUp(whathnd)

        # print(whathnd)
        # print(finup)

        # frame restriction of hand movement
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # Mod mouse movement
        if finup[0] == 0 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 0:
            # Coordinate conversion for the screen
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothing the mouse
            clockX = clockX + (x3 - plocX) / smooth
            clockY = clockY + (y3 - plocY) / smooth

            # Mouse movement
            mouse.move(clockX, clockY)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            plocX, plocY = clockX, clockY

        # Left mouse button
        if finup[0] == 0 and finup[1] == 1 and finup[2] == 1 and finup[3] == 0 and finup[4] == 0:
            length, img, _ = detector.findDistance(8, 12, img)
            # print(length)
            # Mouse click if the distance is less than 25
            if length > 25:
                flag = True
            if length < 25 and flag == True:
                func.LCM(img, x1, y1, length)
                flag = False

        # Right mouse button
        if finup[0] == 0 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 1:
            length, img, _ = detector.findDistance(8, 20, img)
            # print(length)

            # Mouse click if the distance is less than 50
            if length > 30:
                flag = True
            if length < 50:
                func.RCM(img, x1, y1, length)
                flag = False

        # Grub and drop
        if finup[0] == 1 and finup[1] == 1 and finup[2] == 1 and finup[3] == 0 and finup[4] == 0:
            length, img, _ = detector.findDistance(8, 12, img)
            # print(length)
            if length < 25:
                mouse.press(button="left")
                mouse.move(clockX, clockY)

        # scroll
        if finup[0] == 1 and finup[1] == 0 and finup[2] == 0 and finup[3] == 0 and finup[4] == 0:
            if len(lmList) != 0:
                x1, y1 = lmList[4][1:]
                x2, y2 = lmList[5][1:]
                if y1 > y2:
                    mouse.wheel(delta=-0.5)
                elif y1 < y2:
                    mouse.wheel(delta=0.5)

        # Distance
        #if len(lmList) != 0:
            #coord17x, coord17y = lmList[17][1:]
            #coord0x, coord0y = lmList[0][1:]
            #distanse170 = int(np.sqrt((coord0y - coord17y) ** 2 + (coord0x - coord17x) ** 2))
            #distanse170cm = 5503.9283512 * distanse170 ** (-1.0016171)
            #print(distanse170,distanse170cm)
            #cv2.putText(img, f'{str(int(distanse170cm))}cm', (20, 90), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # angle of inclination + distance
        if len(lmList)!=0:
            coord17x, coord17y = lmList[17][1:]
            coord0x, coord0y = lmList[0][1:]
            coord5x, coord5y = lmList[5][1:]
            distanse170 = int(np.sqrt((coord0y - coord17y) ** 2 + (coord0x - coord17x) ** 2))
            distanse50 = int(np.sqrt((coord0y - coord5y) ** 2 + (coord0x - coord5x) ** 2))
            ratio = distanse50/distanse170
            shx = coord17x-coord0x
            shy = coord17y-coord0y
            ratioalpha= np.arctan(-0.4)
            alphaplusbeta = np.arctan(shx/shy)
            ratiobeta = alphaplusbeta-ratioalpha
            shxnew = (shx*np.cos(ratiobeta)) + (shy*np.sin(ratiobeta))
            shynew = (-shx*np.sin(ratiobeta))+(shy*np.cos(ratiobeta))
            ratioXY = abs(shxnew/shynew)
            constratioXY = abs(-0.4)

            #new distance
            if ratioXY >= constratioXY:
                l = shxnew*np.sqrt(1+(1/constratioXY)**2)
                distanse170cm = 5503.9283512 * l ** (-1.0016171)
            else:
                l = shynew*np.sqrt(1+constratioXY**2)
                distanse170cm = 5503.9283512 * l ** (-1.0016171)

            difference = 1.1-ratio

            #old distance
            if abs(difference)<1:
                distanse170cmold = 5503.9283512 * distanse170 ** (-1.0016171)
                print(distanse170cm, distanse170cmold, shx,shy,shxnew,shynew, ratiobeta, l)
                cv2.putText(img, f'{str(int(distanse170cmold))}cm', (20, 90), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)






        # Sound settings
        if finup[0] == 1 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 1:
            length, img, _ = detector.findDistance(4, 8, img)
            #func.chngVol(length, minVol, maxVol, volume, distanse170cm)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # Display
        cv2.imshow("Hand tracking", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
