import RPi.GPIO as GPIO
import time
import socket
import threading
import os

HOST = "192.168.0.100"
PORT = 6543
DELAY = 0.0055


class RaspiControl:
    """
    Class that represents single RaspberryPI singleboard computer, that perform communication with Gelbots software
    and controls steppers, SFL and laser.
    """
    coilx_enable = 35
    coilx_direction = 37
    coilx_step = 33
    coily_enable = 19
    coily_direction = 21
    coily_step = 15
    coil_laser = 40
    shutter = 36
    valve = 38

    def __init__(self, host, port, delay):
        self.HOST = host
        self.PORT = port
        self.DELAY = delay
        self.requests_list = []
        GPIO.setmode(GPIO.BOARD)
        # set PINs mode
        GPIO.setup(self.coilx_enable, GPIO.OUT)
        GPIO.setup(self.coilx_direction, GPIO.OUT)
        GPIO.setup(self.coilx_step, GPIO.OUT)
        GPIO.setup(self.coily_enable, GPIO.OUT)
        GPIO.setup(self.coily_direction, GPIO.OUT)
        GPIO.setup(self.coily_step, GPIO.OUT)
        GPIO.setup(self.shutter, GPIO.OUT)
        GPIO.setup(self.valve, GPIO.OUT)
        GPIO.setup(self.coil_laser, GPIO.OUT)
        # setup default output values
        GPIO.output(self.valve, GPIO.HIGH)
        GPIO.output(self.shutter, GPIO.LOW)
        GPIO.output(self.coil_laser, GPIO.HIGH)
        # setup threads
        self.stop_blink_thread = threading.Event()
        self.stop_sfl_thread = threading.Event()
        self.stop_stamping_thread = threading.Event()
        self.blink_thread = threading.Thread(target=self.blink, args=(0, 0, self.stop_blink_thread))
        self.sfl_thread = threading.Thread(target=self.sfl, args=(0, 0, 0, 0, self.stop_sfl_thread))
        self.stamping_thread = threading.Thread(target=self.stamp, args=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                                         self.stop_stamping_thread))

    def move_x(self, steps):
        """
        Function that controls stepping of X axis stepper
        :param steps: number of desired steps for X axis stepper
        :return: None
        """
        GPIO.output(self.coilx_enable, GPIO.HIGH)
        if steps < 0:
            GPIO.output(self.coilx_direction, GPIO.LOW)
        else:
            GPIO.output(self.coilx_direction, GPIO.HIGH)
        time.sleep(0.05)
        for i in range(abs(steps)):
            GPIO.output(self.coilx_step, 1)
            time.sleep(0.001)
            GPIO.output(self.coilx_step, 0)

    def move_y(self, steps):
        """
        Function that controls stepping of Y axis stepper
        :param steps: number of desired steps for Y axis stepper
        :return: None
        """
        GPIO.output(self.coily_enable, GPIO.HIGH)
        if steps < 0:
            GPIO.output(self.coily_direction, GPIO.LOW)
        else:
            GPIO.output(self.coily_direction, GPIO.HIGH)
        time.sleep(0.05)
        for i in range(abs(steps)):
            GPIO.output(self.coily_step, 1)
            time.sleep(0.001)
            GPIO.output(self.coily_step, 0)

    def one_pulse(self, on_time, off_time):
        """
        Function that perform single SFL light pulse
        :param on_time: SFL light time on [ms]
        :param off_time: following time off of the SFL light [ms]
        :return: None
        """
        GPIO.output(self.shutter, GPIO.HIGH)
        time.sleep(on_time / 1000)
        GPIO.output(self.shutter, GPIO.LOW)
        time.sleep(off_time / 1000)

    def blink_n(self, on_period, off_period, n):
        """
        Function for blinking laser control. The blink is performed n-times.
        :param on_period: laser time on [ms]
        :param off_period: laser time off [ms]
        :param n: number of light pulses [-]
        :return: None
        """
        for i in range(n):
            GPIO.output(self.laser_coil, GPIO.LOW)
            time.sleep(on_period / 1000)
            GPIO.output(self.laser_coil, GPIO.HIGH)
            time.sleep(off_period / 1000)

    def blink(self, on_period, off_period, stop_pill):
        """
        Function for unlimited laser blinking. It is associated to its own thread.
        :param on_period: laser time on [ms]
        :param off_period: laser time off [ms]
        :param stop_pill: signal for thread termination
        :return: None
        """
        while not stop_pill.wait(0.01):
            GPIO.output(self.laser_coil, GPIO.HIGH)
            time.sleep(off_period / 1000)
            GPIO.output(self.laser_coil, GPIO.LOW)
            time.sleep(on_period / 1000)

    def sfl(self, flush_on, flush_off, light_on, light_off, stop_pill):
        """
        Function that controls automatic and periodic SFL. This function is associated to its own thread.
        :param flush_on: time on of flushing [ms]
        :param flush_off: time off of flushing [ms]
        :param light_on: time on for SFL light [ms]
        :param light_off: time off for SFL light [ms]
        :param stop_pill: signal for thread termination
        :return: None
        """
        while not stop_pill.wait(0.01):
            GPIO.output(self.shutter, GPIO.HIGH)
            time.sleep(light_on / 1000)
            GPIO.output(self.shutter, GPIO.LOW)
            time.sleep(light_off / 1000)
            GPIO.output(self.valve, GPIO.LOW)
            time.sleep(flush_on / 1000)
            GPIO.output(self.valve, GPIO.HIGH)
            time.sleep(flush_off / 1000)

    def red_button(self):
        """
        Function that emulate RED BUTTON function. It setups outputs of the RaspBerryPI to SAFE states and terminates
        the python script (all running threads also).
        :return: None
        """
        used_pins = (self.coilx_enable, self.coilx_direction, self.coilx_step, self.coily_enable,
                     self.coily_direction, self.coily_step, self.coil_laser, self.valve, self.shutter)
        GPIO.output(used_pins, GPIO.LOW)
        GPIO.output(self.coil_laser, GPIO.HIGH)
        GPIO.output(self.valve, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.cleanup()
        # TODO TEST sudo pkill -9 python
        command = 'pkill -9 python'
        os.popen("sudo -S %s" % command, 'w').write('mypass')

    def stamp(self,dx, dy, steps_x, steps_y, delay_x, delay_y, light_on, light_off, sfl_on, sfl_off, batch, stop_pill):
        for i in range(batch):
            for j in range(steps_x):
                print("stepping in x")
                for k in range(steps_y - 1):
                    if stop_pill.wait(0.001):
                        return
                    print("stepping in y")
                    # light on
                    GPIO.output(self.shutter, GPIO.HIGH)
                    time.sleep(light_on / 1000)
                    # light off
                    GPIO.output(self.shutter, GPIO.LOW)
                    # move in y
                    GPIO.output(self.coily_enable, GPIO.HIGH)
                    print("movey")
                    if dy < 0:
                        GPIO.output(self.coily_direction, GPIO.LOW)
                    else:
                        GPIO.output(self.coily_direction, GPIO.HIGH)
                    time.sleep(0.05)
                    for i in range(abs(dy)):
                        GPIO.output(self.coily_step, 1)
                        time.sleep(0.001)
                        GPIO.output(self.coily_step, 0)
                    time.sleep(delay_y / 1000)

                # light on
                GPIO.output(self.shutter, GPIO.HIGH)
                time.sleep(light_on / 1000)
                # light off
                GPIO.output(self.shutter, GPIO.LOW)
                # move in y back
                time.sleep(light_off / 1000)
                print("moving back in y")
                GPIO.output(self.coily_enable, GPIO.HIGH)
                print("movey")
                steps = -1 * dy * (steps_y - 1)
                if steps < 0:
                    GPIO.output(self.coily_direction, GPIO.LOW)
                else:
                    GPIO.output(self.coily_direction, GPIO.HIGH)
                time.sleep(0.05)
                for i in range(abs(steps)):
                    GPIO.output(self.coily_step, 1)
                    time.sleep(0.001)
                    GPIO.output(self.coily_step, 0)
                time.sleep(delay_y / 1000)
                # move dx
                print("moving in x")
                GPIO.output(self.coilx_enable, GPIO.HIGH)
                if j < steps_x - 1:
                    print("movex")
                    if dx < 0:
                        GPIO.output(self.coilx_direction, GPIO.LOW)
                    else:
                        GPIO.output(self.coilx_direction, GPIO.HIGH)
                    time.sleep(0.05)
                    for i in range(abs(dx)):
                        GPIO.output(self.coilx_step, 1)
                        time.sleep(0.001)
                        GPIO.output(self.coilx_step, 0)
                    time.sleep(delay_x / 1000)
            # return to start
            print("return to start position")
            GPIO.output(self.coilx_enable, GPIO.HIGH)
            print("movex")
            steps = dx * -1 * (steps_x - 1)
            if steps < 0:
                GPIO.output(self.coilx_direction, GPIO.LOW)
            else:
                GPIO.output(self.coilx_direction, GPIO.HIGH)
            time.sleep(0.05)
            for i in range(abs(steps)):
                GPIO.output(self.coilx_step, 1)
                time.sleep(0.001)
                GPIO.output(self.coilx_step, 0)
            time.sleep(delay_y / 1000)
            # flush on
            print("flush on")
            GPIO.output(self.valve, GPIO.LOW)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                while True:
                    try:
                        data = conn.recv(100)
                        if len(data) > 0:
                            data_decode = data.decode("UTF-8")
                            self.requests_list.extend(filter(None, data_decode.split(";")))
                    except Exception as ex:
                        if len(self.requests_list) == 0:
                            break

                    if len(self.requests_list) > 0:
                        decoded = self.requests_list.pop()
                        if decoded[0] == "x":
                            self.move_x(steps=int(decoded[1:]))
                        elif decoded[0] == "y":
                            self.move_y(steps=int(decoded[1:]))
                        elif decoded[0] == "l":
                            GPIO.output(self.coil_laser, GPIO.HIGH)
                        elif decoded[0] == "s":
                            GPIO.output(self.coil_laser, GPIO.LOW)
                        elif decoded[0] == "k":
                            on_time = int(decoded.split(",")[1])
                            off_time = int(decoded.split(",")[2])
                            self.stop_blink_thread.clear()
                            self.blink_thread = threading.Thread(target=self.blink, args=(on_time, off_time,
                                                                                          self.stop_blink_thread))
                            self.blink_thread.start()
                        elif decoded[0] == "t":
                            self.stop_blink_thread
                        elif decoded[0] == "r":
                            self.stop_blink_thread.set()
                            self.stop_sfl_thread.set()
                            self.stop_stamping_thread.set()
                            time.sleep(0.1)
                            self.requests_list = []
                            self.red_button()
                            # TODO: red button. set all outputs to LOW, terminate laser thread
                        elif decoded[0] == "q":
                            on_time = int(decoded.split(",")[1])
                            off_time = int(decoded.split(",")[2])
                            n = int(decoded.split(",")[3])
                            self.blink_n(on_time, off_time, n)
                        elif decoded[0] == "p":
                            flush_on = int(decoded.split(",")[1])
                            flush_off = int(decoded.split(",")[2])
                            light_on = int(decoded.split(",")[3])
                            light_off = int(decoded.split(",")[4])
                            self.stop_sfl_thread.clear()
                            self.sfl_thread = threading.Thread(target=self.sfl,
                                                          args=(
                                                          flush_on, flush_off, light_on, light_off,
                                                          self.stop_sfl_thread))
                            self.sfl_thread.start()
                        elif decoded[0] == "h":
                            GPIO.output(self.shutter, GPIO.LOW)
                        elif decoded[0] == "j":
                            GPIO.output(self.shutter, GPIO.HIGH)
                        elif decoded[0] == "n":
                            GPIO.output(self.valve, GPIO.LOW)
                        elif decoded[0] == "m":
                            GPIO.output(self.valve, GPIO.HIGH)
                        elif decoded[0] == "a":
                            on_time = int(decoded.split(",")[1])
                            wait_time = int(decoded.split(",")[2])
                            self.one_pulse(on_time, wait_time)
                        elif decoded[0] == "c":
                            self.stop_stamping_thread.set()
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
                            self.stop_stamping_thread.clear()
                            self.stamping_thread = threading.Thread(target=self.stamp,
                                                          args=(dx, dy, steps_x, steps_y, delay_x, delay_y, light_on,
                                                                light_off,
                                                                sfl_on, sfl_off, batch, self.stop_stamping_thread))
                            self.stamping_thread.start()
                        data = None
            GPIO.cleanup()


if __name__ == "__main__":
    raspi = RaspiControl(HOST, PORT,DELAY)
    raspi.run()
    print("exiting...")