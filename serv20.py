import RPi.GPIO as GPIO
import time
import socket
import threading


def stamp(dx, dy, steps_x, steps_y, delay_x, delay_y, light_on, light_off, sfl_on, sfl_off, batch, stop_pill):
    coilx_enable = 35
    coilx_direction = 37
    coilx_step = 33

    coily_enable = 19
    coily_direction = 21
    coily_step = 15
    laser_coil = 40

    shutter = 36
    valve = 38
    print("dx", dx)
    print("dy", dy)
    print("starting stamping mode")

    for i in range(batch):
        print("batch n.:", batch)
        for j in range(steps_x):
            print("stepping in x")
            for k in range(steps_y - 1):
                if stop_pill.wait(0.001):
                    return
                print("stepping in y")
                # light on
                GPIO.output(shutter, GPIO.HIGH)
                time.sleep(light_on / 1000)
                # light off
                GPIO.output(shutter, GPIO.LOW)
                # move in y
                GPIO.output(coily_enable, GPIO.HIGH)
                print("movey")
                if dy < 0:
                    GPIO.output(coily_direction, GPIO.LOW)
                else:
                    GPIO.output(coily_direction, GPIO.HIGH)
                time.sleep(0.05)
                for i in range(abs(dy)):
                    GPIO.output(coily_step, 1)
                    time.sleep(0.001)
                    GPIO.output(coily_step, 0)
                time.sleep(delay_y / 1000)

            # light on
            GPIO.output(shutter, GPIO.HIGH)
            time.sleep(light_on / 1000)
            # light off
            GPIO.output(shutter, GPIO.LOW)
            # move in y back
            time.sleep(light_off / 1000)
            print("moving back in y")
            GPIO.output(coily_enable, GPIO.HIGH)
            print("movey")
            steps = -1 * dy * (steps_y - 1)
            if steps < 0:
                GPIO.output(coily_direction, GPIO.LOW)
            else:
                GPIO.output(coily_direction, GPIO.HIGH)
            time.sleep(0.05)
            for i in range(abs(steps)):
                GPIO.output(coily_step, 1)
                time.sleep(0.001)
                GPIO.output(coily_step, 0)
            time.sleep(delay_y / 1000)
            # move dx
            print("moving in x")
            GPIO.output(coilx_enable, GPIO.HIGH)
            if j < steps_x - 1:
                print("movex")
                if dx < 0:
                    GPIO.output(coilx_direction, GPIO.LOW)
                else:
                    GPIO.output(coilx_direction, GPIO.HIGH)
                time.sleep(0.05)
                for i in range(abs(dx)):
                    GPIO.output(coilx_step, 1)
                    time.sleep(0.001)
                    GPIO.output(coilx_step, 0)
                time.sleep(delay_x / 1000)
        # return to start
        print("return to start position")
        GPIO.output(coilx_enable, GPIO.HIGH)
        print("movex")
        steps = dx * -1 * (steps_x - 1)
        if steps < 0:
            GPIO.output(coilx_direction, GPIO.LOW)
        else:
            GPIO.output(coilx_direction, GPIO.HIGH)
        time.sleep(0.05)
        for i in range(abs(steps)):
            GPIO.output(coilx_step, 1)
            time.sleep(0.001)
            GPIO.output(coilx_step, 0)
        time.sleep(delay_y / 1000)
        # flush on
        print("flush on")
        GPIO.output(valve, GPIO.LOW)
        time.sleep(sfl_on / 1000)
        # flush off
        print("flush off")
        GPIO.output(valve, GPIO.HIGH)
        time.sleep(sfl_off / 1000)


def one_pulse(on_time, wait_time, shutter):
    print("shutter", shutter)
    print(on_time)
    print(wait_time)
    GPIO.output(shutter, GPIO.HIGH)
    time.sleep(on_time / 1000)
    GPIO.output(shutter, GPIO.LOW)
    time.sleep(wait_time / 1000)


def light_control(shutter, value):
    if value > 0:
        GPIO.output(shutter, GPIO.LOW)
    else:
        GPIO.output(shutter, GPIO.LOW)


def move_x(steps, coilx_enable, coilx_direction, coilx_step):
    GPIO.output(coilx_enable, GPIO.HIGH)
    print("movex")
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
    print("movey")
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
        time.sleep(on_period / 1000)
        GPIO.output(laser_coil, GPIO.HIGH)
        time.sleep(off_period / 1000)
        stop_time = time.time()


def blink(on_period, off_period, laser_coil, stop_pill):
    print("enterint thread")
    while not stop_pill.wait(0.01):
        GPIO.output(laser_coil, GPIO.LOW)
        time.sleep(on_period / 1000)
        GPIO.output(laser_coil, GPIO.HIGH)
        time.sleep(off_period / 1000)
        stop_time = time.time()


def sfl(flush_on, flush_off, light_on, light_off, valve, shutter, stop_pill):
    print("sfl thread")
    while not stop_pill.wait(0.01):
        GPIO.output(shutter, GPIO.HIGH)
        time.sleep(light_on / 1000)
        GPIO.output(shutter, GPIO.LOW)
        time.sleep(light_off / 1000)
        GPIO.output(valve, GPIO.LOW)
        time.sleep(flush_on / 1000)
        GPIO.output(valve, GPIO.HIGH)
        time.sleep(flush_off / 1000)


GPIO.setmode(GPIO.BOARD)
delay = 0.0055
HOST = "192.168.0.100"
PORT = 6543

coilx_enable = 35
coilx_direction = 37
coilx_step = 33

coily_enable = 19
coily_direction = 21
coily_step = 15
coil_laser = 40

shutter = 36
valve = 38

used_pins = (coilx_enable, coilx_direction, coilx_step, coily_enable,
             coily_direction, coily_step, coil_laser, valve, shutter)

GPIO.setup(coilx_enable, GPIO.OUT)
GPIO.setup(coilx_direction, GPIO.OUT)
GPIO.setup(coilx_step, GPIO.OUT)

GPIO.setup(coily_enable, GPIO.OUT)
GPIO.setup(coily_direction, GPIO.OUT)
GPIO.setup(coily_step, GPIO.OUT)

GPIO.setup(shutter, GPIO.OUT)
GPIO.setup(valve, GPIO.OUT)


def red_button(used_pins):
    GPIO.output(used_pins, GPIO.LOW)
    GPIO.output(coil_laser, GPIO.HIGH)
    GPIO.output(valve, GPIO.HIGH)
    GPIO.output(shutter, GPIO.LOW)


GPIO.output(valve, GPIO.HIGH)
GPIO.output(shutter, GPIO.LOW)
GPIO.setup(coil_laser, GPIO.OUT)
GPIO.output(coil_laser, GPIO.HIGH)

thread_pool = []
stop_thread = threading.Event()
stop_thread2 = threading.Event()
stop_thread3 = threading.Event()
my_thread = threading.Thread(target=blink, args=(0, 0, coil_laser, stop_thread))
my_thread2 = threading.Thread(target=sfl, args=(0, 0, 0, 0, valve, shutter, stop_thread2))
my_thread3 = threading.Thread(target=stamp, args=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stop_thread3))
# socket.setdefaulttimeout(.1)
requests_list = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        # try:
        conn, addr = s.accept()
        # print("connected")
        # except Exception as ex:
        #    pass

        while True:
            # time.sleep(0.1)
            try:
                data = conn.recv(50)
                if len(data) > 0:
                    print(data)
                    data_decode = data.decode("UTF-8")
                    requests_list.extend(filter(None, data_decode.split(";")))
                    print("requests list:", requests_list)
            except Exception as ex:
                if len(requests_list) == 0:
                    # GPIO.output(coil_laser, GPIO.LOW)
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
                    stop_thread2.set()
                    stop_thread3.set()
                    time.sleep(0.1)
                    requests_list = []
                    red_button(used_pins)
                    # TODO: red button. set all outputs to LOW, terminate laser thread
                elif decoded[0] == "q":
                    on_time = int(decoded.split(",")[1])
                    off_time = int(decoded.split(",")[2])
                    n = int(decoded.split(",")[3])
                    blink_n(on_time, off_time, coil_laser, n)
                elif decoded[0] == "p":
                    flush_on = int(decoded.split(",")[1])
                    flush_off = int(decoded.split(",")[2])
                    light_on = int(decoded.split(",")[3])
                    light_off = int(decoded.split(",")[4])
                    stop_thread2.clear()
                    my_thread2 = threading.Thread(target=sfl,
                                                  args=(flush_on, flush_off, light_on, light_off, valve, shutter,
                                                        stop_thread2))
                    my_thread2.start()
                elif decoded[0] == "h":
                    GPIO.output(shutter, GPIO.LOW)
                elif decoded[0] == "j":
                    GPIO.output(shutter, GPIO.HIGH)
                elif decoded[0] == "n":
                    GPIO.output(valve, GPIO.LOW)
                elif decoded[0] == "m":
                    GPIO.output(valve, GPIO.HIGH)
                elif decoded[0] == "a":
                    on_time = int(decoded.split(",")[1])
                    wait_time = int(decoded.split(",")[2])
                    one_pulse(on_time, wait_time, shutter)
                elif decoded[0] == "c":
                    stop_thread3.set()
                elif decoded[0] == "b":
                    # batch
                    dx = int(decoded.split(",")[1])
                    dy = int(decoded.split(",")[2])
                    steps_x = int(decoded.split(",")[3])
                    steps_y = int(decoded.split(",")[4])
                    delay_x = int(decoded.split(",")[5])
                    delay_y = int(decoded.split(",")[6])
                    light_on = int(decoded.split(",")[7])
                    light_off = int(decoded.split(",")[8])
                    sfl_on = int(decoded.split(",")[9])
                    sfl_off = int(decoded.split(",")[10])
                    batch = int(decoded.split(",")[11])
                    stop_thread3.clear()
                    my_thread3 = threading.Thread(target=stamp,
                                                  args=(dx, dy, steps_x, steps_y, delay_x, delay_y, light_on, light_off,
                                                        sfl_on, sfl_off, batch, stop_thread3))
                    my_thread3.start()
                data = None
GPIO.cleanup()