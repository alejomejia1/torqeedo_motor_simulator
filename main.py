import threading
from flask import Flask, render_template, jsonify
import serial
import time
from apscheduler.schedulers.background import  BackgroundScheduler
from torqeedo_motor_sim.torqeedo_motor_sim import TorqeedoMotorSim

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True
    
lm = TorqeedoMotorSim('leftMotor','/dev/cu.SLAB_USBtoUART6',1000,600,3270) # name, port, rpm, power, battery
rm = TorqeedoMotorSim('rightMotor','/dev/cu.SLAB_USBtoUART10',600,-600,3270)

def leftMotor():
    lm.state_machine()

def rightMotor():
    rm.state_machine()
            
sched = BackgroundScheduler(daemon=True)
sched.add_job(leftMotor, 'interval', seconds=.01)
sched.add_job(rightMotor, 'interval', seconds=.01)
sched.start()


app = Flask(__name__)

command=bytearray()
command.clear()

# interval example

    
    
@app.route("/")
def dashboard():
    return render_template('base.html', lm = lm, rm = rm)

@app.route("/get_motors_status", methods=['GET'])
def getMotorsStatus():
    lmRpm = lm.rpm;
    response = {
        "leftMotor":{
            "rpm":lm.rpm,
            "power": lm.power,
            "battery": lm.bat
        },
        "rightMotor":{
            "rpm":rm.rpm,
            "power": rm.power,
            "battery": rm.bat
        }
    }            
    return jsonify(response)                   

if __name__ == '__main__':
      app.run(port=5000)

# Also make sure that nothing else is running on port 80