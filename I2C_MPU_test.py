# import smbus
# import math
# 
# def main():
# 	mpu6150 = MPU6150(0x68)
# 	
# class MPU6150:
# 
# 	#G lobal Variables
# 	GRAVITY_MS2 = 9.80665
# 	address = None
# 	bus = smbus.SMBus(1)
# 	
# 	#Scale Modifiers
# 	GYRO_SCALE_MODIFIER_250DEG=131.0
# 	GYRO_SCALE_MODIFIER_500DEG = 65.5
# 	GYRO_SCALE_MODIFIER_1000DEG = 32.8
# 	GYRO_SCALE_MODIFIER_2000DEG = 16.4
# 	
# 	#Predefine ranges
# 	GYRO_RANGE_250DEG=0x00
# 	GYRO_RANGE_500DEG = 0x08
# 	GYRO_RANGE_1000DEG = 0x10
# 	GYRO_RANGE_2000DEG = 0x18
# 	
# 	#MPU-6050 Registers
# 	PWR_MGMT_1 = 0x6B
# 	PWR_MGMT_2 = 0x6C
# 	GYRO_XOUT0 = 0x43
# 	GYRO_YOUT0 = 0x45
# 	GYRO_ZOUT0 = 0x47
# 	GYRO_CONFIG = 0X1B
# 	print('algo')
# 	
# 	def __init__(self,address):
# 		self.address = address
# 		print('Starting MPU...')
# 		#Wake up the MPU-9150 since it starts in sleep mode 
# 		self.bus.write_byte_data(self.address,self.PWR_MGMT_1,0x00)
# 		print('MPU successfully started')
# 		
		
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

def contar():
    global counter
    while 1:
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
    #if value>35768:
    #    value = value-65536
    return value

bus = smbus.SMBus(1)
Device_Address = 0x68
MPU_initialization()

threading.Thread(target=contar).start()

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
    
    #print(counter)

    deltaT = counter - Tprev
    Tprev = counter
    
    Accel_Angle_X=math.atan(Ax/math.sqrt(Ay**2+Az**2))*(180.0/3.14)
    Accel_Angle_Y=math.atan(Ay/math.sqrt(Ax**2+Az**2))*(180.0/3.14)
    Comp_Angle_X=0.96*(Gyro_Angle_X_pre+((Gx)*deltaT))+0.04*Accel_Angle_X
    Comp_Angle_Y=0.96*(Gyro_Angle_Y_pre+((Gy)*deltaT))+0.04*Accel_Angle_Y
    Gyro_Angle_X_pre = Comp_Angle_X
    Gyro_Angle_Y_pre=Comp_Angle_Y
    print(", ",Comp_Angle_X,", ",Comp_Angle_Y)
    print(", ","0.0")

    #print("Acceleraton: X=%.2fg\t\t" %Ax, "Y=%.2fg\t" %Ay, "Z=%.2fg" %Az)
    #print("Gs Rotation: Gx=%.2f\xb0/s\t" %Gx, "Gy=%.2f\xb0/s\t" %Gy, "Gz=%.2f\xb0/s" %Gz) 
 

    time.sleep(0.5)
		
#if __name__ =='__main__':
#	try:
#		main()
#	except KeyboardInterrupt:
#		pass
		
