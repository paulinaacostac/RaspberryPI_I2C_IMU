#Matrix libraries
#Para correr utilizar sudo python3 luma_SPI_test.py
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi,noop
from luma.core.render import canvas
#sudo pip3 install keyboard
import keyboard
import time
global puntox
global puntoy

import time 
import smbus
import threading
import math

global counter
counter =0
deltaT = 0
Tprev=0
Accel_X_RAW = 0
Accel_Y_RAW=0
Accel_Z_RAW = 0
Gyro_X_RAW = 0
Gyro_Y_RAW=0
Gyro_Z_RAW = 0
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

puntox=3
puntoy=3


#Luma
class Matrix(object):
    def __init__(self):
        super(Matrix,self).__init__()
        self.device=self.create_matrix_device(1,0,0)
    def create_matrix_device(self,n,block_orientation,rotate):
        #Create matrix device
        print("Creating device...")
        serial=spi(port=0,device=0,gpio=noop())
        device=max7219(serial,cascaded=n,block_orientation=block_orientation,rotate=rotate)
        print("Device created.")
        return device
    def draw_point(self,x,y):
        with canvas(self.device) as draw:
            draw.point((x,y),fill="green")
    def draw_rectangle(self,x,y,x1,y1):
        with canvas(self.device) as draw:
            draw.rectangle((x,y,x1,y1),fill="green")


#MPU
def contar():
    global counter
    while 1:
        time.sleep(100)
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



if __name__ == "__main__":
    try:
              
        bus = smbus.SMBus(1)
        Device_Address = 0x68
        MPU_initialization()
        threading.Thread(target=contar).start()


        matrix = Matrix()
        x_act=5
        y_act=-0.7
        lim_inf_X=4.97
        lim_sup_X=5.02
        lim_inf_Y=-0.8
        lim_sup_Y=-0.6
        deltaPos= 1
        
        while 1:
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
            

            deltaT = counter - Tprev
            Tprev = counter
            
            Accel_Angle_X=math.atan(Ax/math.sqrt(Ay**2+Az**2))*(180.0/3.14)
            Accel_Angle_Y=math.atan(Ay/math.sqrt(Ax**2+Az**2))*(180.0/3.14)
            Comp_Angle_X=0.96*(Gyro_Angle_X_pre+((Gx)*deltaT))+0.04*Accel_Angle_X
            Comp_Angle_Y=0.96*(Gyro_Angle_Y_pre+((Gy)*deltaT))+0.04*Accel_Angle_Y
            Gyro_Angle_X_pre = Comp_Angle_X
            Gyro_Angle_Y_pre=Comp_Angle_Y
            
            print('Comp_Angle_X: ',Comp_Angle_X,' Comp_Angle_Y: ',Comp_Angle_Y)
            
            if (Comp_Angle_X>=lim_inf_X and Comp_Angle_X<=lim_sup_X) and (Comp_Angle_Y>=lim_inf_Y and Comp_Angle_Y<=lim_sup_Y):
                matrix.draw_rectangle(3,3,4,4)
            
            if Comp_Angle_X < x_act-deltaPos:
                if puntox<7:
                    puntox+=1
                matrix.draw_rectangle(puntoy,puntox,puntoy-1,puntox-1)
                x_act = x_act-deltaPos
            
            if Comp_Angle_X>x_act+deltaPos:
                if puntox>1:
                    puntox-=1
                matrix.draw_rectangle(puntoy,puntox,puntoy-1,puntox-1)
                x_act = x_act+deltaPos
            
            if Comp_Angle_Y<y_act-deltaPos:
                if puntoy<7:
                    puntoy+=1
                matrix.draw_rectangle(puntoy,puntox,puntoy-1,puntox-1)
                y_act = y_act-deltaPos
                
            if Comp_Angle_Y>y_act+deltaPos:
                if puntoy>1:
                    puntoy-=1
                matrix.draw_rectangle(puntoy,puntox,puntoy-1,puntox-1)
                y_act = y_act+deltaPos

            #time.sleep(0.5)

    except KeyboardInterrupt:
        pass


