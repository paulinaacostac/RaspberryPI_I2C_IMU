#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import serial

import time 
import smbus
import threading
import math

global counter
# global bus
# global Device_Address
# global PWR_MGT_1,CONFIG,SAMPLE_RATE,GYRO_CONFIG,ACCEL_CONFIG,Gyro_Angle_X_pre,Gyro_Angle_Y_pre
# global deltaT,Tprev
# global ACCEL_X_HIGH,ACCEL_Y_HIGH,ACCEL_Z_HIGH,GYRO_X_HIGH,GYRO_Y_HIGH,GYRO_Z_HIGH,TEMP_OUT_HIGH
counter =0
deltaT = 0
Tprev=0

Gyro_Angle_X_pre = 0
Gyro_Angle_Y_pre=0

PWR_MGT_1 = 0x6B
CONFIG = 0x1A
SAMPLE_RATE = 0x19
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_X_HIGH = 0x3B
ACCEL_Y_HIGH = 0x3D
ACCEL_Z_HIGH = 0x3F
GYRO_X_HIGH = 0x43
GYRO_Y_HIGH = 0x45
GYRO_Z_HIGH = 0x47
TEMP_OUT_HIGH = 0x41

########################################################################
########################################################################
##
##  SOLO ES NECESARIO ESPECIFICAR EL PUERTO DEL STM32 Y LOS BAUDIOS
##
########################################################################
########################################################################

# ser = serial.Serial('/dev/tty.usbserial', 38400, timeout=1)
#ser = serial.Serial('COM3', 115200, timeout=1)


########################################################################
########################################################################
ax = ay = az = 0.0
yaw_mode = False

def contar():
    global counter
    while 1:
        time.sleep(1)
        counter+=1

def MPU_initialization():
    bus.write_byte_data(Device_Address, PWR_MGT_1, 0x00)
    bus.write_byte_data(Device_Address, SAMPLE_RATE, 0x07)
    bus.write_byte_data(Device_Address, CONFIG, 0x00)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 0x00)

def Read_data(reg_add):
    high = bus.read_byte_data(Device_Address, reg_add)
    low = bus.read_byte_data(Device_Address, reg_add+1)
    value = (high<<8)|low
    if value>35768:
        value = value-65536
    return value

def resize(width, height):
    if height == 0:
       height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0 * width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def drawText(position, textString):
    font = pygame.font.SysFont("Courier", 18, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


def draw():
    global rquad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax))

    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawText((0.2, 1.7, 2), osd_line)

    # the way I'm holding the IMU board, X and Y axis are switched
    # with respect to the OpenGL coordinate system
    if yaw_mode:  # experimental
        glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    else:
        glRotatef(0.0, 0.0, 1.0, 0.0)
    glRotatef(ay, 1.0, 0.0, 0.0)  # Pitch, rotate around x-axis
    glRotatef(-1 * ax, 0.0, 0.0, 1.0)  # Roll,  rotate around z-axis

    glBegin(GL_QUADS)
    glColor3f(0, 0.8706, 1)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(0, 0.8706, 1)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(0.4, 0.58, 0.60)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(0.4, 0.58, 0.60)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.4, 0.58, 0.60)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(0.4, 0.58, 0.60)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()



video_flags = OPENGL | DOUBLEBUF

pygame.init()
screen = pygame.display.set_mode((640, 480), video_flags)
#pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
pygame.display.set_caption("GyroAnimation")
resize(640, 480)
init()
frames = 0
ticks = pygame.time.get_ticks()
bus = smbus.SMBus(1)
Device_Address = 0x68
MPU_initialization()
while 1:
    threading.Thread(target=contar).start()
    ACCEL_X = Read_data(ACCEL_X_HIGH)
    ACCEL_Y = Read_data(ACCEL_Y_HIGH)
    ACCEL_Z = Read_data(ACCEL_Z_HIGH)
    GYRO_X = Read_data(GYRO_X_HIGH)
    GYRO_Y = Read_data(GYRO_Y_HIGH)
    GYRO_Z = Read_data(GYRO_Z_HIGH)

    Ax = ACCEL_X/16384.0
    Ay = ACCEL_Y/16384.0
    Az = ACCEL_Z/16384.0

    Gx = GYRO_X/131.0
    Gy = GYRO_Y/131.0
    Gz = GYRO_Z/131.0
    
    #print(counter)

    deltaT = counter - Tprev
    Tprev = counter
    
    Accel_Angle_X=math.atan(Ax/math.sqrt(Ay**2+Az**2))*(180.0/3.14)
    Accel_Angle_Y=math.atan(Ay/math.sqrt(Ax**2+Az**2))*(180.0/3.14)
    #Comp_Angle_X=0.96*(Gyro_Angle_X_pre+((Gx)*deltaT))+0.04*Accel_Angle_X
    #Comp_Angle_Y=0.96*(Gyro_Angle_Y_pre+((Gy)*deltaT))+0.04*Accel_Angle_Y
    #Gyro_Angle_X_pre = Comp_Angle_X
    #Gyro_Angle_Y_pre=Comp_Angle_Y
     
    #ax=(Comp_Angle_X*-1)/1000
    #ay=(Comp_Angle_Y*-1)/100
    #az=(Comp_Angle_Y)/100
    
    ax=Accel_Angle_Y
    ay=Accel_Angle_X
    #az=Accel_Angle_X
    
    
    
    print(ax," ",ay," ",az)
    
    
    event = pygame.event.poll()

    #pygame.image.save(pygame.display.get_surface(), "animation2.png")

    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        pygame.quit()  # * quit pygame properly
        break
    if event.type == KEYDOWN and event.key == K_z:
        yaw_mode = not yaw_mode
        ser.write(b"z")
    
    
    draw()

    pygame.display.flip()
    frames = frames + 1

print("fps:  %d" % ((frames * 1000) / (pygame.time.get_ticks() - ticks)))
ser.close()



if __name__ == '__main__': main()