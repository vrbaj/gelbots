import RPi.GPIO as GPIO
import time
import socket
import threading


def move_x(steps, coilx_enable, coilx_direction, coilx_step):
    GPIO.output(coilx_enable, GPIO.HIGH)
    if steps < 0:
        GPIO.output(coilx_direction, GPIO.LOW)
    else:
        GPIO.output(coilx_direction, GPIO.HIGH)
    time.sleep(0.05)
    for i in range(abs(steps)):
        GPIO.output(coilx_step, 1)
        time.sleep(0.001)
        GPIO.output(coilx_step, 0)

def move_y(steps, coily_enable, coily_direction, coily_step):
    GPIO.output(coily_enable, GPIO.HIGH)
    if steps < 0:
        GPIO.output(coily_direction, GPIO.LOW)
    else:
        GPIO.output(coily_direction, GPIO.HIGH)
    time.sleep(0.05)
    for i in range(abs(steps)):
        GPIO.output(coily_step, 1)
        time.sleep(0.001)
        GPIO.output(coily_step, 0)


def blink(on_period, off_period, laser_coil, stop_pill):
    print("run blink thread")
    while not stop_pill.wait(1):
    
        GPIO.output(laser_coil, GPIO.HIGH)
        time.sleep(on_period)
        GPIO.output(laser_coil, GPIO.LOW)
        time.sleep(off_period)
    

GPIO.setmode(GPIO.BOARD)
delay = 0.0055
HOST = "10.0.0.29"
PORT = 6543

coilx_enable = 33
coilx_direction = 33
coilx_step = 33

coily_enable = 35
coily_direction = 35
coily_step = 35
coil_laser = 37

used_pins = (coilx_enable, coilx_direction, coilx_step, coily_enable,
             coily_direction, coily_step, coil_laser)

GPIO.setup(coilx_enable, GPIO.OUT)
GPIO.setup(coilx_direction, GPIO.OUT)
GPIO.setup(coilx_step, GPIO.OUT)

GPIO.setup(coily_enable, GPIO.OUT)
GPIO.setup(coily_direction, GPIO.OUT)
GPIO.setup(coily_step, GPIO.OUT)

def red_button(used_pins):
    GPIO.output(used_pins, GPIO.LOW)



GPIO.setup(coil_laser, GPIO.OUT)
GPIO.output(coil_laser, GPIO.LOW)

thread_pool = []
stop_thread = threading.Event()
my_thread = threading.Thread(target=blink, args=(0, 0, coil_laser, stop_thread))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        while True:
            try:
                data = conn.recv(10)
            except Exception as ex:
                print("disconnect")
                GPIO.output(coil_laser, GPIO.LOW)
                break
            if len(data) > 0:
                decoded = data.decode("UTF-8")
                print("data:", decoded)
                if decoded[0] == "x":
                    move_x(int(decoded[1:]), coilx_enable, coilx_direction, coilx_step)
                elif decoded[0] == "y":
                    move_y(int(decoded[1:]), coily_enable, coily_direction, coily_step)
                elif decoded[0] == "l":
                    GPIO.output(coil_laser, GPIO.HIGH)
                elif decoded[0] == "s":
                    GPIO.output(coil_laser, GPIO.LOW)
                elif decoded[0] == "k":
                    on_time = int(decoded.split(",")[1])
                    off_time = int(decoded.split(",")[2])
                    
                    my_thread = threading.Thread(target=blink,
                                                 args=(on_time, off_time, coil_laser, stop_thread))
                    my_thread.start()
                    
                elif decoded[0] == "t":
                    # TODO: terminate laser thread
                    stop_thread.set()
                elif decoded[0] == "r":
                    stop_thread.set()
                    red_button(used_pins)
                    # TODO: red button. set all outputs to LOW, terminate laser thread
                data = None
GPIO.cleanup()