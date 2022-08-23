import cv2
import pyautogui as pag
import mediapipe as mp
import mouse
import numpy as np
import time
import HandTrackingModule as htm
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


#Запуск окна камеры + константы
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
wCam, hCam = 640, 480
cam.set(3, wCam)
cam.set(4, hCam)

pTime = 0

detector = htm.handDetector(maxHands=1)

wScr, hScr = pag.size()
#print(wScr, hScr) # вывод размера экрана
frameR = 150 #Уменьшение вводимого окна

smooth = 3 #сглаживание мыши
plocX,plocY = 0,0
clockX, clockY = 0,0
#############################################
#Volume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
#############################################

#Начало фактической логики
while True:
    success, img = cam.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #Отслеживаем положение указательного и большого пальца
    if len(lmList)!=0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[4][1:]
        #print(x1,y2,x2,y2) #вывод координат 4,8 точки т.е большого и указательного пальца

    #Чекаем какая рука
    whathnd = detector.whatHand()
    #Чекаем поднят ли палец
    finup = detector.fingersUp(whathnd)
    print(whathnd)
    print(finup)

    #рамка ограничение движения руки7
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

    #Мод движения мыши, проверка поднятого указательного пальца
    if finup[1]==1 and finup[0]==0 and finup[2]==0 and finup[3]==0 and finup[4]==0:
        #Преобразование координат для экрана
        x3= np.interp(x1,(frameR,wCam-frameR),(0,wScr))
        y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

        #Сглаживание мыши
        clockX=  clockX + (x3 - plocX) / smooth
        clockY = clockY + (y3 - plocY) / smooth

        #Движение мышки
        mouse.move(wScr-clockX,clockY)
        cv2.circle(img,(x1,y1),10,(0,0,255),cv2.FILLED)
        plocX,plocY = clockX,clockY

    #Левая кнопка мыши
    if finup[1] == 1 and finup[2] == 1 and finup[0] == 0 and finup[3] == 0 and finup[4] == 0:
        length, img, _ = detector.findDistance(8, 12, img)
        print(length)
        #Клик мышкой если расстояник меньше 25
        if length < 25:
            cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
            mouse.click('left')
            while length <25 == True:
                time.sleep(0.3)

    #Правая кнопка мыши
    if finup[1] == 1 and finup[4] == 1 and finup[0] == 0 and finup[2] == 0 and finup[3] == 0:
        length, img, _ = detector.findDistance(8, 20, img)
        #print(length)
        #Клик мышкой если расстояник меньше 21
        if length < 30:
            cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
            mouse.click(button='right')
            time.sleep(0.45)

    #Настройка звука
    if finup[0] == 1 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 1:
        length, img, _ = detector.findDistance(4, 8, img)
        vol = np.interp(length, [-100, 180], [minVol, maxVol])
        print(length,vol)
        volume.SetMasterVolumeLevel(vol, None)


    #FPS
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    #Display
    cv2.imshow("Hand tracking", img)
    cv2.waitKey(1)