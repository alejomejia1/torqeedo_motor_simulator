from celery import Celery
from celery.utils.log import get_task_logger
import time, datetime
import serial

broker_heartbeat=0
app = Celery('simulator', backend='rpc://', broker='amqp://guest@localhost//')

logger = get_task_logger('simulator')

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

def crc8(stream):
    crc = 0
    for c in stream:
        for i in range(0, 8):
            b = (crc & 1) ^ ((( int(c) & (1 << i))) >> i)
            crc = (crc ^ (b * 0x118)) >> 1
    return(hex(crc))

def hex_to_string(hex):
    if hex[:2] == '0x':
        hex = hex[2:]
    string_value = bytes.fromhex(hex).decode('utf-8')
    return string_value

def motor_status_data(status_flags, error_flags):
    status = REQ_MOTOR_STATUS_FROM_BATT_TO_MOTOR
    status[2] = status_flags
    status[3] = error_flags >> 8
    status[4] = error_flags & 0x00ff
    return status
    
ser = serial.Serial('cu.SLAB_USBtoUART', 19200, timeout=0.001)
print(ser.name)         # check which port was really used
print("Best regards from torqeedo motor simulator.\nNow i will transmit data to host...");

command=bytearray()
command.clear()

@app.task
def uppercaseme(value):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info('Got {0} now: {1}'.format(value, now))
    logger.info('Working hard on uppercasing...')
    time.sleep(30)
    return value.upper()

@app.task
def lowercaseme(value):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info('Got {0} now: {1}'.format(value, now))
    logger.info('Working hard on lowercasing...')
    time.sleep(30)
    return value.lower()