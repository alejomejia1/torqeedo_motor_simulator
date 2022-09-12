import sys
import serial
import time
import codecs

REQ_SPEED_FROM_BATT_TO_REMOTE=							bytearray([	0xac,	#header 
															0x14, 0x01,	#frame identifier
															0x89,	#CRC
															0xad])	#footer
REQ_MOTOR_STATUS_FROM_BATT_TO_MOTOR=					bytearray([	0xac, #header
															0x30, 0x01, #frame identifier
															0x73, #CRC
															0xad])	#footer
SEND_MOTOR_STATUS_FROM_MOTOR_TO_BATT=					bytearray([	0xac, #header
															0x00, 0x00, 0x00, 0x00, 0x00, 0x00,	#info 
															0xad, 0x00])	#footer
REQ_MOTOR_PARAMETERS_FROM_BATT_TO_MOTOR=				bytearray([	0xac,	#header
															0x30, 0x03,	#frame identifier
															0xcf,	#CRC
															0xad])	#footer
SEND_MOTOR_PARAMETERS_FROM_MOTOR_TO_BATT=				bytearray([	0xac,	#header 
															0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c, 	#info 
                                                          	0xae, 0x2d, 0x00, 0x00, 0x01, 0x42, 0x06, 0xa4, 	#info 
                                                           	0xea,	#CRC
                                                            0xad, 0x00])	#footer
SEND_MOTOR_POWER_ORDER_FROM_BATT_TO_MOTOR=			bytearray([	0xac,	#header
															0x30, 0x82, 0x00, 0x00, 0x00,	##frame identifier
															0x00,	#info 
															0xa5,	#CRC 
                                                          	0xad])	#footer
SEND_MOTOR_POWER_ORDER_ACK_FROM_MOTOR_TO_BATT=		bytearray([	0xac,	#header 
                                                          	0x00, 0x00,	#frame identifier
                                                           	0x00,	#CRC
                                                           	0xad, 0x00])	#footer

SEND_SYSTEM_STATE_FROM_LCD_TO_BATT=					bytearray([	0xac,	#header 
                                                          	0x20, 0x41,	#frame identifier
                                                           	0x00, 0x00,	#flags
															0x00,				#master_state
															0x00,				#master_error_code
															0x0c, 0xc6,	#motor_voltage 32.7V (3270*0.01)
															0x00, 0x00,	#motor_current
															0x00, 0x00,	#motor_power
															0x00, 0xec,	#motor_rpm 236
															0x00,				#motor_pcb_temp
															0x00,				#motor_stator_temp
															0x56,				#batt_charge_pct 86
															0x00, 0x00,	#batt_voltage
															0x00, 0x00,	#batt_current
															0x00, 0x00,	#gps_speed
															0x00, 0x00,	#range_miles
															0x00, 0x00,	#range_minutes
															0x00, 			#temp_sw
															0x00, 			#temp_rp
															0x00,	#CRC
                                                           	0xad, 0x00])	#footer


class TorqeedoMotorSim: 
    def __init__(self, name, port, rpm, power, bat):
        self.name = name
        self.port = port
        self.ser = serial.Serial(port, 19200, timeout=0.001)
        self.command = bytearray()
        self.command.clear()
        self.prevRxState=0;
        self.rxState=0
        self.sendMotorOrder=False
        self.delayCounter=0
        self.timerCount=0
        self.timerMaxCount=5
        self.timerShoot=False
        self.events=0
        self.framesTxState=0
        self.frameNrToTx=0;
        self.frameByteArrayToTx=bytearray()
        self.t0=time.perf_counter_ns()
        self._flags = 0x0000
        self._master_status = 0x00
        self._master_error_code = 0x00
        self._motor_voltage = 0x0cc6 # 32.7 Volts (3270)
        self._motor_current = 0x0000
        self._rpm = rpm
        self._power = power
        self._bat = bat
        self._motor_pcb_temp = 0x00
        self._motor_stator_temp = 0x00
        self._bat_volage = 0x0000
        self._bat_current = 0x0000
        self._gps_speed = 0x0000
        self._range_miles = 0x0000
        self._range_minutes = 0x0000
        self._temp_sw = 0x00
        self._temp_rp = 0x00
        self._status = 0x0000


    @property
    def motor_pcb_temp(self):
        return self._motor_pcb_temp
    
    @motor_pcb_temp.setter
    def motor_pcb_temp(self, motor_pcb_temp):
        self._motor_pcb_temp = motor_pcb_temp
        
    @property
    def motor_stator_temp(self):
        return self._motor_stator_temp
    
    @motor_stator_temp.setter
    def motor_stator_temp(self, motor_stator_temp):
        self._motor_stator_temp = motor_stator_temp
        
    @property
    def motor_stator_temp(self):
        return self._motor_stator_temp
    
    @motor_stator_temp.setter
    def motor_stator_temp(self, motor_stator_temp):
        self._motor_stator_temp = motor_stator_temp

    @property
    def bat_volage(self):
        return self._bat_volage
    
    @bat_volage.setter
    def bat_volage(self, bat_volage):
        self._bat_volage = bat_volage
        
    @property
    def bat_current(self):
        return self._bat_current
    
    @bat_current.setter
    def bat_current(self, bat_current):
        self._bat_current = bat_current
        
    @property
    def gps_speed(self):
        return self._gps_speed
    
    @gps_speed.setter
    def gps_speed(self, gps_speed):
        self._gps_speed = gps_speed
        
    @property
    def range_miles(self):
        return self._range_miles
    
    @range_miles.setter
    def range_miles(self, range_miles):
        self._range_miles = range_miles

    @property
    def range_minutes(self):
        return self._range_minutes
    
    @range_minutes.setter
    def range_minutes(self, range_minutes):
        self._range_minutes = range_minutes
        
    @property
    def rpm(self):
        return self._rpm
    
    @rpm.setter
    def rpm(self, rpm):
        self._rpm = rpm
    
    @property
    def power(self):
        return self._power
    
    @power.setter
    def power(self, power):
        self._power = power
        
    @property
    def bat(self):
        return self._bat
    
    @bat.setter
    def bat(self, bat):
        self._bat = bat
    
    @property
    def error(self):
        return self._error
    
    @error.setter
    def error(self, error):
        self._error = error
    
    def crc8(self, stream):
        crc = 0
        for c in stream:
            for i in range(0, 8):
                b = (crc & 1) ^ ((( int(c) & (1 << i))) >> i)
                crc = (crc ^ (b * 0x118)) >> 1
        return(crc)
    
    def hex_to_string(self, hex):
        if hex[:2] == '0x':
            hex = hex[2:]
        string_value = bytes.fromhex(hex).decode('utf-8')
        return string_value

    def motor_status_data(self, status_flags, error_flags):
        status = SEND_MOTOR_STATUS_FROM_MOTOR_TO_BATT
        status[2] = status_flags
        status[3] = error_flags >> 8
        status[4] = error_flags & 0x00ff
        crc = self.crc8(status[2:4])
        status[5] = crc
        return status

    def system_state_data(self, flags, master_state, master_error, motor_voltage, motor_current, motor_power, motor_rpm, motor_pcb_temp, motor_stator_temp, bat_perc, bat_voltage, bat_current, gps_speed, range_miles, range_minutes, temp_sw, temp_rp):
        status = SEND_SYSTEM_STATE_FROM_LCD_TO_BATT
        status[3] = flags >> 8
        status[4] = flags & 0x00ff
        status[5] = master_state
        status[6] = master_error
        status[7] = motor_voltage >> 8
        status[8] = motor_voltage & 0x00ff
        status[9] = motor_current >> 8
        status[10] = motor_current & 0x00ff
        status[11] = motor_power >> 8
        status[12] = motor_power & 0x00ff
        status[13] = motor_rpm >> 8
        status[14] = motor_rpm & 0x00ff
        status[15] = motor_pcb_temp
        status[16] = motor_stator_temp
        status[17] = bat_perc
        status[18] = bat_voltage >> 8
        status[19] = bat_voltage & 0x00ff
        status[20] = bat_current >> 8
        status[21] = bat_current & 0x00ff
        status[22] = gps_speed >> 8
        status[23] = gps_speed & 0x00ff
        status[24] = range_miles >> 8
        status[25] = range_miles & 0x00ff
        status[26] = range_minutes >> 8
        status[27] = range_minutes & 0x00ff
        status[28] = temp_sw
        status[29] = temp_rp
        crc = self.crc8(status[2:28])
        status[30] = crc
        # print(crc)
        return status
    
    
    def map_master_error_code_to_string(self, error_code):
        match error_code:
            case 2:
                return "stator high temp"
            case 5:
                return "propeller blocked"
            case 6:
                return "motor low voltage"
            case 7:
                return "motor high current"
            case 8:
                return "pcb temp high"
            case 21:
                return "tiller cal bad"
            case 22:
                return "mag bad"
            case 23:
                return "range incorrect"
            case 30:
                return "motor comm error"
            case 32:
                return "tiller comm error"
            case 33:
                return "general comm error"
            case 41:
                return "charge voltage bad"
            case 42:
                return "charge voltage bad"
            case 43:
                return "battery flat"
            case 45:
                return "battery high current"
            case 46:
                return "battery temp error"
            case 48:
                return "charging temp error"
            case _:
                return "Code not found"
            
  
    def parse_message(self,msg):
        byteObj = bytes(msg)
        # print(byteObj[2], byteObj[3])
        if (byteObj[2] == 0 and byteObj[3]== 0):
            cmd = byteObj[6:8]
            pwr = int.from_bytes(cmd, "big", signed=True)
            self._power = pwr
            print(pwr)
        
        
    def state_machine(self):
        self.t1=time.perf_counter_ns()
        if self.t1-self.t0>=(10*1000000):	#10 ms
            self.t0=self.t1
            self.timerShoot=True
        
        if self.timerShoot==True:
            self.timerShoot=False;
            self.timerCount+=1

            if self.timerCount>=self.timerMaxCount:
                self.timerCount=0;

                if self.frameNrToTx==0:
                    self.frameByteArrayToTx=REQ_SPEED_FROM_BATT_TO_REMOTE
                    self.timerMaxCount=2
                elif self.frameNrToTx==1:
                    self.frameByteArrayToTx=REQ_MOTOR_STATUS_FROM_BATT_TO_MOTOR
                    self.timerMaxCount=2
                elif self.frameNrToTx==2:
                    self.frameByteArrayToTx=self.motor_status_data(0x00, 0x00)
                    self.timerMaxCount=2
                elif self.frameNrToTx==3:
                    self.frameByteArrayToTx=REQ_MOTOR_PARAMETERS_FROM_BATT_TO_MOTOR
                    self.timerMaxCount=2
                elif self.frameNrToTx==4:
                    self.frameByteArrayToTx=SEND_MOTOR_PARAMETERS_FROM_MOTOR_TO_BATT
                    self.timerMaxCount=2
                elif self.frameNrToTx==5:
                    self.frameByteArrayToTx=SEND_MOTOR_POWER_ORDER_FROM_BATT_TO_MOTOR
                    self.timerMaxCount=2
                elif self.frameNrToTx==6:
                    self.frameByteArrayToTx=SEND_MOTOR_POWER_ORDER_ACK_FROM_MOTOR_TO_BATT
                    self.timerMaxCount=2
                elif self.frameNrToTx==7:
                    self.frameByteArrayToTx=SEND_SYSTEM_STATE_FROM_LCD_TO_BATT
                    self.timerMaxCount=2
                
                if self.frameNrToTx<7:
                    self.frameNrToTx+=1
                else:
                    self.frameNrToTx=0
                    
                self.ser.write(self.frameByteArrayToTx)
        
        if self.ser.inWaiting():
            self.read=self.ser.read()
            if self.read!=b'':
                if self.rxState==0:
                    if self.read==b'\xac':
                        #print("AC received")
                        self.command.clear()
                        self.rxState=1
                
                elif self.rxState==1:
                    if self.read==b'\xad':
                        #print("AD received")
                        # for i in range (len(self.command)):
                        #     print(hex(self.command[i]), end=" ")
                        # print(" ")
                        self.parse_message(self.command)    
                        self.command.clear()
                        rxState=0
                    else:
                        self.command.append(self.read[0])
