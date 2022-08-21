import cv2
import pyautogui as pag
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule as htm



#Запуск окна камеры + константы
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
wCam, hCam = 640, 480
cam.set(3, wCam)
cam.set(4, hCam)

pTime = 0

detector = htm.handDetector(maxHands=1)

wScr, hScr = pag.size()
#print(wScr, hScr) # вывод размера экрана
frameR = 100 #Уменьшение вводимого окна

smooth = 2 #сглаживание мыши
plocX,plocY = 0,0
clockX, clockY = 0,0

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

    #Чекаем поднят ли палец
    finup = detector.fingersUp()
    #print(finup)

    #рамка ограничение движения руки
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

    #Мод движения мыши, проверка поднятого указательного пальца
    if finup[1]==1 and finup[0]==0 and finup[2]==0:
        #Преобразование координат для экрана
        x3= np.interp(x1,(frameR,wCam-frameR),(0,wScr))
        y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

        #Сглаживание мыши
        clockX=  clockX + (x3 - plocX) / smooth
        clockY = clockY + (y3 - plocY) / smooth

        #Движение мышки
        pag.moveTo(wScr-clockX, clockY)
        cv2.circle(img,(x1,y1),10,(0,0,255),cv2.FILLED)
        plocX,plocY = clockX,clockY

    #Левая кнопка мыши77
    if finup[1] == 1 and finup[0] == 1:
        length, img, _ = detector.findDistance(8, 4, img)
        print(length)
        #Клик мышкой если расстояник меньше 21
        if length < 21:
            cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
            pag.click()
            pass

    #Правая кнопка мыши
    if finup[1] == 1 and finup[2] == 1:
        length, img, _ = detector.findDistance(8, 12, img)
        print(length)
        #Клик мышкой если расстояник меньше 21
        if length < 21:
            cv2.circle(img, (x1, y1), 10, (0, 255, 255), cv2.FILLED)
            pag.click(button='right')
            pass

    #FPS
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    #Display
    cv2.imshow("Hand tracking", img)
    cv2.waitKey(1)
