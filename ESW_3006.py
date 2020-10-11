import numpy as np
import argparse
import math
import cv2
import serial
import time
import sys
from threading import Thread

serial_use = 1

serial_port = None
Read_RX = 0
receiving_exit = 1
threading_Time = 0.01

W_View_size = 640
H_View_size = int(W_View_size / 1.333)  # 480

FPS = 90  # PI CAMERA: 320 x 240 = MAX 90

View_select = 1

cap = cv2.VideoCapture(0)
cap.set(3, W_View_size)
cap.set(4, H_View_size)
cap.set(5, FPS)

Serial_stat = 0
Serial_stat_old = Serial_stat

# *******************************************************
# *************************************************
# ---------------------color check-----------------
# ----------------------Yellow----------------------
y_H_down = 15
y_H_up = 50
y_S_down = 80
y_S_up = 255
y_V_down = 90
y_V_up = 255
# ----------------------Red----------------------
r_H_down = 0
r_H_up = 20
r_S_down = 80
r_S_up = 255
r_V_down = 60
r_V_up = 255
# ----------------------Blue----------------------
b_H_down = 80
b_H_up = 130
b_S_down = 45
b_S_up = 250
b_V_down = 0
b_V_up = 180
# ----------------------Green----------------------
g_H_down = 15
g_H_up = 50
g_S_down = 80
g_S_up = 255
g_V_down = 90
g_V_up = 255


# *******************************************************
# *******************************************************

# -----------------------------------------------
def TX_data_py2(ser, one_byte):  # one_byte= 0~255

    # ser.write(chr(int(one_byte)))          #python2.7
    ser.write(serial.to_bytes([one_byte]))  # python3


def RX_data(ser):
    if ser.inWaiting() > 0:
        result = ser.read(1)
        RX = ord(result)
        return RX
    else:
        return 0


def Sending(num):
    # serial_port.flush()
    TX_data_py2(serial_port, int(num))
    print("Send : " + str(num))
    time.sleep(0.1)


def Receiving(ser):
    global receiving_exit

    receiving_exit = 1
    while True:
        if receiving_exit == 0:
            break
        time.sleep(threading_Time)
        while ser.inWaiting() > 0:
            result = ser.read(1)
            RX = ord(result)
            RX = str(RX)
            print("RX=" + RX)
            if RX == "0": receiving_exit = 0


def Serial_L_and_R(num):  # 6 : left // 7 : right
    global Serial_stat
    global Serial_stat_old

    Serial_stat = num
    if Serial_stat != Serial_stat_old:
        Sending(Serial_stat)
        Receiving(serial_port)
        Serial_stat_old = Serial_stat


def Serial_G():
    global Serial_stat
    global Serial_stat_old

    Serial_stat = 2
    if Serial_stat != Serial_stat_old:
        Sending(Serial_stat)
        Receiving(serial_port)
        Serial_stat_old = Serial_stat


# ---------------------------------------------
def nothing(x):
    pass


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked


# .......................................................................................

# .....  num=0  ..........................................................................
def Line_T():  # line_T
    # Serial_L_and_R(5)
    Serial_L_and_R(29)
    global num

    time.sleep(0.5)
    while (1):
        ret, img_color = cap.read()

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)
        vertices_2 = np.array(
            [[0 + 100, 0], [W_View_size - 100, 0], [W_View_size - 100, H_View_size / 2], [0 + 100, H_View_size / 2]],
            np.int32)
        roi_2 = roi(img_gray, [vertices_2])
        contours2, _ = cv2.findContours(roi_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours2) > 0:
            cnt2 = contours2[0]
            hull2 = cv2.convexHull(cnt2)
            mmt2 = cv2.moments(hull2)

            if mmt2['m00'] > 0:
                cx2 = int(mmt2['m10'] / mmt2['m00'])
                cy2 = int(mmt2['m01'] / mmt2['m00'])
                cv2.imshow('roi_2', roi_2)
                if cy2 > 180:
                    num = 1
                    break
                if cx2 <= 230:
                    Serial_L_and_R(6)
                elif cx2 >= 410:
                    Serial_L_and_R(7)
                else:
                    Serial_G()

        cv2.imshow('Yellow', img_yellow)
        cv2.imshow('roi2', roi_2)

        key = 0xFF & cv2.waitKey(1)
        if key == 27:  # ESC  Key
            break

    Serial_L_and_R(1)
    cv2.destroyAllWindows()


# .....  num=1  ..........................................................................
def Line_T2():  # line_T2
    global num
    time.sleep(0.5)

    while (1):
        ret, img_color = cap.read()

        cx3 = -1
        cy3 = -1
        cx4 = -1
        cy4 = -1

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)

        vertices_3 = np.array([[0, 0], [200, 0], [200, H_View_size], [0, H_View_size]], np.int32)
        roi_3 = roi(img_gray, [vertices_3])
        contours3, _ = cv2.findContours(roi_3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        vertices_4 = np.array(
            [[W_View_size - 200, 0], [W_View_size, 0], [W_View_size, H_View_size], [W_View_size - 200, H_View_size]],
            np.int32)
        roi_4 = roi(img_gray, [vertices_4])
        contours4, _ = cv2.findContours(roi_4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours3) > 0:
            cnt3 = contours3[0]
            hull3 = cv2.convexHull(cnt3)
            mmt3 = cv2.moments(hull3)
            if mmt3['m00'] > 0:
                cx3 = int(mmt3['m10'] / mmt3['m00'])
                cy3 = int(mmt3['m01'] / mmt3['m00'])

        if len(contours4) > 0:
            cnt4 = contours4[0]
            hull4 = cv2.convexHull(cnt4)
            mmt4 = cv2.moments(hull4)
            if mmt4['m00'] > 0:
                cx4 = int(mmt4['m10'] / mmt4['m00'])
                cy4 = int(mmt4['m01'] / mmt4['m00'])
        if cy3 < 140 and cy4 < 140:
            num = 0
            break
        if cy3 > 0 or cy4 > 0:
            if cy3 > 0 and cy4 < 0:
                Serial_L_and_R(21)

            elif cy3 < 0 and cy4 > 0:
                Serial_L_and_R(22)
            else:
                if cy3 - cy4 > 100:
                    Serial_L_and_R(21)
                elif cy3 - cy4 < -100:
                    Serial_L_and_R(22)
                else:
                    num = 3
                    break

        cv2.imshow('Yellow', img_color)

        key = 0xFF & cv2.waitKey(1)
        if key == 27:  # ESC  Key
            break

    Serial_L_and_R(1)
    cv2.destroyAllWindows()


# ....  num=2   .................................................................
def NSWE():  # NSWE
    Serial_L_and_R(9)
    time.sleep(1)
    pause = False
    global num

    while True:
        if pause == False:
            ret, img_color = cap.read()

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        ret, img_binary = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if pause == True:
            for cnt in contours:
                size = len(cnt)

                epsilon = 0.005 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                size = len(approx)

                cnt = contours[0]
                hull = cv2.convexHull(cnt)
                x, y, w, h = cv2.boundingRect(hull)

                if 12 <= size <= 16:
                    if w < 200:
                        print(str(size) + "E")
                        Serial_L_and_R(13)
                        num = 0
                        break
                    else:
                        print(str(size) + "W")
                        Serial_L_and_R(14)
                        num = 0
                        break
                elif 27 <= size <= 30:
                    print(str(size) + "S")
                    Serial_L_and_R(12)
                    num = 0
                    break
                elif 9 <= size <= 11:
                    print(str(size) + "N")
                    Serial_L_and_R(11)
                    num = 0
                    break
                else:
                    print(str(size) + "Error")
                    num = 2
                    break
                break
            break

        cv2.imshow('original', img_color)

        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break
        elif key == ord(' '):  # spacebar Key
            if pause == True:
                pause = False
            else:
                pause = True

    cv2.destroyAllWindows()


# .....   num=3   ..............................................
def arrow():
    Serial_L_and_R(9)
    time.sleep(1)
    pause = False

    global num

    while (1):
        if pause == False:
            ret, img_color = cap.read()

        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        ret, img_binary = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow('bianry', img_binary)

        if pause == True:
            img_color2 = img_color.copy()
            contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                for cnt in contours:
                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    size = len(approx)
                    cnt = contours[0]
                    hull = cv2.convexHull(cnt)
                    mmt = cv2.moments(hull)
                    if mmt['m00'] > 0:
                        cx = int(mmt['m10'] / mmt['m00'])
                        cy = int(mmt['m01'] / mmt['m00'])
                        if cx > 400:
                            Serial_L_and_R(7)
                            pause = False
                        elif cx < 200:
                            Serial_L_and_R(6)
                            pause = False
                        else:
                            vertices_1 = np.array(
                                [[cx, H_View_size], [W_View_size, H_View_size], [W_View_size, 0], [cx, 0]], np.int32)
                            roi_1 = roi(img_binary, [vertices_1])
                            contours1, _ = cv2.findContours(roi_1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            if len(contours1) > 0:
                                for cnt in contours1:
                                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                                    size = len(approx)

                                    if 3 <= size <= 5:
                                        Serial_L_and_R(15)
                                        num = 4
                                        pause = False
                                        break
                                    else:
                                        Serial_L_and_R(17)
                                        num = 6
                                        pause = False
                                        break
                    break
            break
        cv2.imshow('bianry', img_binary)

        key = 0xFF & cv2.waitKey(1)
        if key == 27:  # ESC  Key
            break
        elif key == ord(' '):  # spacebar Key
            if pause == True:
                pause = False
            else:
                pause = True

    cv2.destroyAllWindows()


# *************************************************************
# *************************************************************

# ....   num=4    ................LEFT....................
def Line_clock():
    Serial_L_and_R(29)
    time.sleep(1)

    global num

    while (1):
        ret, img_color = cap.read()

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)
        vertices_2 = np.array(
            [[0 + 100, 0], [W_View_size - 100, 0], [W_View_size - 100, H_View_size / 2], [0 + 100, H_View_size / 2]],
            np.int32)
        roi_2 = roi(img_gray, [vertices_2])
        contours2, _ = cv2.findContours(roi_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours2) > 0:
            cnt2 = contours2[0]
            hull2 = cv2.convexHull(cnt2)
            mmt2 = cv2.moments(hull2)

            if mmt2['m00'] > 0:
                cx2 = int(mmt2['m10'] / mmt2['m00'])
                cy2 = int(mmt2['m01'] / mmt2['m00'])

                if cy2 > 160:
                    num = 5
                    break
                if cx2 <= 230:
                    Serial_L_and_R(6)
                elif cx2 >= 410:
                    Serial_L_and_R(7)
                else:
                    Serial_G()

        cv2.imshow('roi_2', roi_2)
        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break
    cv2.destroyAllWindows()


# ....   num=5    ................LEFT....................
def Line_clock2():
    global num

    while (1):
        ret, img_color = cap.read()

        cx4 = -1
        cy4 = -1

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)
        vertices_2 = np.array(
            [[0 + 100, 0], [W_View_size - 100, 0], [W_View_size - 100, H_View_size / 2], [0 + 100, H_View_size / 2]],
            np.int32)
        roi_2 = roi(img_gray, [vertices_2])
        contours2, _ = cv2.findContours(roi_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        vertices_4 = np.array(
            [[W_View_size - 100, 0], [W_View_size, 0], [W_View_size, H_View_size], [W_View_size - 100, H_View_size]],
            np.int32)
        roi_4 = roi(img_gray, [vertices_4])
        contours4, _ = cv2.findContours(roi_4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours4) > 0:
            cnt4 = contours4[0]
            hull4 = cv2.convexHull(cnt4)
            mmt4 = cv2.moments(hull4)
            if mmt4['m00'] > 0:
                cx4 = int(mmt4['m10'] / mmt4['m00'])
                cy4 = int(mmt4['m01'] / mmt4['m00'])

        if len(contours2) > 0:
            cnt2 = contours2[0]
            hull2 = cv2.convexHull(cnt2)
            mmt2 = cv2.moments(hull2)
            if mmt2['m00'] > 0:
                cx2 = int(mmt2['m10'] / mmt2['m00'])
                cy2 = int(mmt2['m01'] / mmt2['m00'])
                print('222222', cx2, cy2, "\n4444444", cx4, cy4)
                if cy4 < 140:
                    num = 4
                    break
                if cx2 <= 230:
                    if cy4 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_L_and_R(6)
                elif cx2 >= 410:
                    if cy4 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_L_and_R(7)
                else:
                    if cy4 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_G()
            break

        cv2.imshow('roi_2', roi_2)
        cv2.imshow('roi_4', roi_4)
        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break

    cv2.destroyAllWindows()


# *************************************************************
# *************************************************************

# ....   num=6     ...............Right.......................
def Line_count_clock():
    Serial_L_and_R(29)

    global num

    while (1):
        ret, img_color = cap.read()

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)
        vertices_2 = np.array(
            [[0 + 100, 0], [W_View_size - 100, 0], [W_View_size - 100, H_View_size / 2], [0 + 100, H_View_size / 2]],
            np.int32)
        roi_2 = roi(img_gray, [vertices_2])
        contours2, _ = cv2.findContours(roi_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours2) > 0:
            cnt2 = contours2[0]
            hull2 = cv2.convexHull(cnt2)
            mmt2 = cv2.moments(hull2)

            if mmt2['m00'] > 0:
                cx2 = int(mmt2['m10'] / mmt2['m00'])
                cy2 = int(mmt2['m01'] / mmt2['m00'])

                if cy2 > 160:
                    num = 7
                    break
                if cx2 <= 230:
                    Serial_L_and_R(6)
                elif cx2 >= 410:
                    Serial_L_and_R(7)
                else:
                    Serial_G()

        cv2.imshow('roi_2', roi_2)
        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break
    cv2.destroyAllWindows()


# ....   num=7    ................Right....................
def Line_count_clock2():
    global num

    while (1):
        ret, img_color = cap.read()

        cx3 = -1
        cy3 = -1

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        y_mask = cv2.inRange(img_hsv, np.array([y_H_down, y_S_down, y_V_down]), np.array([y_H_up, y_S_up, y_V_up]))
        img_yellow = cv2.bitwise_and(img_color, img_color, mask=y_mask)

        img_gray = cv2.cvtColor(img_yellow, cv2.COLOR_BGR2GRAY)
        vertices_2 = np.array(
            [[0 + 100, 0], [W_View_size - 100, 0], [W_View_size - 100, H_View_size / 2], [0 + 100, H_View_size / 2]],
            np.int32)
        roi_2 = roi(img_gray, [vertices_2])
        contours2, _ = cv2.findContours(roi_2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        vertices_3 = np.array(
            [[0, 0], [100, 0], [100, H_View_size], [0, H_View_size]],
            np.int32)
        roi_3 = roi(img_gray, [vertices_3])
        contours3, _ = cv2.findContours(roi_3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours3) > 0:
            cnt3 = contours3[0]
            hull3 = cv2.convexHull(cnt3)
            mmt3 = cv2.moments(hull3)
            if mmt3['m00'] > 0:
                cx3 = int(mmt3['m10'] / mmt3['m00'])
                cy3 = int(mmt3['m01'] / mmt3['m00'])

        if len(contours2) > 0:
            cnt2 = contours2[0]
            hull2 = cv2.convexHull(cnt2)
            mmt2 = cv2.moments(hull2)
            if cy3 < 140:
                num = 6
                break
            if mmt2['m00'] > 0:
                cx2 = int(mmt2['m10'] / mmt2['m00'])
                cy2 = int(mmt2['m01'] / mmt2['m00'])
                print("2222", cx2, cy2, "333", cx3, cy3)
                if cx2 <= 230:
                    if cy3 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_L_and_R(6)
                elif cx2 >= 410:
                    if cy3 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_L_and_R(7)
                else:
                    if cy3 > 210:
                        Serial_L_and_R(1)
                        num = 8
                        break
                    else:
                        Serial_G()
            break

        cv2.imshow('roi_2', roi_2)
        cv2.imshow('roi_3', roi_3)
        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break

    Serial_L_and_R(1)
    cv2.destroyAllWindows()


# *************************************************************
# *************************************************************

# ....   num=8    ...........................................
def ABCD():
    Serial_L_and_R(9)
    time.sleep(2)

    pause = False
    global num

    room = [0, 0, 0, 0, 0, 0, 0, 0]
    color = 0
    i = 0

    while True:
        if pause == False:
            ret, img_color = cap.read()

        img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

        R_mask = cv2.inRange(img_hsv, np.array([r_H_down, r_S_down, r_V_down]), np.array([r_H_up, r_S_up, r_V_up]))
        ret1, red = cv2.threshold(R_mask, 127, 255, 0)

        B_mask = cv2.inRange(img_hsv, np.array([b_H_down, b_S_down, b_V_down]), np.array([b_S_up, b_S_up, b_V_up]))
        ret2, blue = cv2.threshold(B_mask, 127, 255, 0)

        if pause == True:
            img_red = cv2.bitwise_and(img_color, img_color, mask=R_mask)
            contours1, _ = cv2.findContours(red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours1) > 0:
                for cnt in contours1:
                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    size = len(approx)

                    cnt = contours1[0]
                    hull = cv2.convexHull(cnt)
                    x, y, w, h = cv2.boundingRect(hull)

                    if 7 <= size <= 10:
                        room[i] = 'A'
                        print(str(size) + "   red_A")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 15 <= size <= 20:
                        room[i] = 'B'
                        print(str(size) + "   red-B")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 22 <= size <= 27:
                        room[i] = 'C'
                        print(str(size) + "   red_C")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 11 <= size <= 14:
                        room[i] = 'D'
                        print(str(size) + "   red_D")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    else:
                        print(str(size) + "   red_ERROR")
                    time.sleep(1)

            img_blue = cv2.bitwise_and(img_color, img_color, mask=B_mask)
            contours2, _ = cv2.findContours(blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours2) > 0:
                for cnt in contours2:
                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    size = len(approx)

                    cnt = contours2[0]
                    hull = cv2.convexHull(cnt)
                    x, y, w, h = cv2.boundingRect(hull)

                    if 7 <= size <= 10:
                        room[i] = 'A'
                        print(str(size) + "   Blue_A")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 15 <= size <= 20:
                        room[i] = 'B'
                        print(str(size) + "   Blue_B")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 24 <= size <= 27:
                        room[i] = 'C'
                        print(str(size) + "   Blue_C")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    elif 11 <= size <= 14:
                        room[i] = 'D'
                        print(str(size) + "   Blue_D")
                        print(str(room[:]))
                        i += 1
                        pause = False
                    else:
                        print(str(size) + "   Blue_ERROR")
                    time.sleep(1)

        cv2.imshow('result', img_color)
        cv2.imshow('red', red)
        cv2.imshow('blue', blue)

        key = 0xFF & cv2.waitKey(1)

        if key == 27:  # ESC  Key
            break
        elif key == ord(' '):  # spacebar Key
            if pause == True:
                pause = False
            else:
                pause = True

    cv2.destroyAllWindows()


# ***************************************************************
# ************main*********************************
if __name__ == '__main__':
    BPS = 4800  # 4800,9600,14400, 19200,28800, 57600, 115200

    serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
    serial_port.flush()  # serial cls

    print('start')

    global num
    num = 0
    pause = False

    while (1):
        if num == 0:
            print('Mode: Line_T')
            Line_T()
        elif num == 1:
            print('Mode: Line_T2')
            Line_T2()
        elif num == 2:
            print('Mode: NSWE')
            NSWE()
        elif num == 3:
            print('Mode: arrow')
            arrow()
        elif num == 4:
            print('Mode: Line_clock')
            Line_clock()
        elif num == 5:
            print('Mode: Line_clock2')
            Line_clock2()
        elif num == 6:
            print('Mode: Line_count_clock')
            Line_count_clock()
        elif num == 7:
            print('Mode: Line_count_clock2')
            Line_count_clock2()
        elif num == 8:
            print('Mode: ABCD')
            ABCD()

        key = 0xFF & cv2.waitKey(1)
        if key == 27:  # ESC  Key
            break

    cap.release()
    cv2.destroyAllWindows()
# **********************************************************
# **********************************************************
