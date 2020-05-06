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

def blink_n(on_period, off_period, laser_coil, n):
    print("n blink")
    for i in range(n):
        GPIO.output(laser_coil, GPIO.LOW)
        time.sleep(on_period/1000)
        GPIO.output(laser_coil, GPIO.HIGH)
        time.sleep(off_period/1000)
        stop_time=time.time()


def blink(on_period, off_period, laser_coil, stop_pill):
    print("enterint thread")
    while not stop_pill.wait(0.01):
        GPIO.output(laser_coil, GPIO.LOW)
        time.sleep(on_period/1000)
        GPIO.output(laser_coil, GPIO.HIGH)
        time.sleep(off_period/1000)
        stop_time=time.time()

GPIO.setmode(GPIO.BOARD)
delay = 0.0055
HOST = "192.168.0.104"
PORT = 6543

coilx_enable = 35
coilx_direction = 37
coilx_step = 33

coily_enable = 19
coily_direction = 21
coily_step = 15
coil_laser = 40

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
    GPIO.output(coil_laser, GPIO.HIGH)



GPIO.setup(coil_laser, GPIO.OUT)
GPIO.output(coil_laser, GPIO.HIGH)

thread_pool = []
stop_thread = threading.Event()
my_thread = threading.Thread(target=blink, args=(0, 0, coil_laser, stop_thread))

#socket.setdefaulttimeout(.1)
requests_list = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    while True:
        #try:
        conn, addr = s.accept()
        #print("connected")
        #except Exception as ex:
        #    pass
            
        while True:
            # time.sleep(0.1)
            try:
                data = conn.recv(50)
                if len(data) > 0 :
                    print(data)
                    data_decode = data.decode("UTF-8")
                    requests_list.extend(filter(None, data_decode.split(";")))
                    print("requests list:", requests_list)
            except Exception as ex:
                if len(requests_list) == 0:
                    
                    #GPIO.output(coil_laser, GPIO.LOW)
                    break
            
            if len(requests_list) > 0:
                decoded = requests_list.pop()
                print(decoded)
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
                    stop_thread.clear()
                    my_thread = threading.Thread(target=blink,
                                                 args=(on_time, off_time, coil_laser, stop_thread))
                    my_thread.start()
                    
                elif decoded[0] == "t":
                    # TODO: terminate laser thread
                    stop_thread.set()
                elif decoded[0] == "r":
                    stop_thread.set()
                    time.sleep(0.1)
                    requests_list = []
                    red_button(used_pins)
                    # TODO: red button. set all outputs to LOW, terminate laser thread
                elif decoded[0] == "q":
                    on_time = int(decoded.split(",")[1])
                    off_time = int(decoded.split(",")[2])
                    n = int(decoded.split(",")[3])
                    blink_n(on_time, off_time, coil_laser, n)
                data = None
GPIO.cleanup()