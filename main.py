import threading
from flask import Flask, render_template
import serial
import time
from apscheduler.schedulers.background import  BackgroundScheduler
from torqeedo_motor_sim import TorqeedoMotorSim

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True
    
lm = TorqeedoMotorSim('leftMotor','/dev/cu.SLAB_USBtoUART')
rm = TorqeedoMotorSim('rightMotor','/dev/cu.SLAB_USBtoUART6')

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
def hello_world():
    return render_template('base.html')


if __name__ == '__main__':
      app.run(port=81)

# Also make sure that nothing else is running on port 80