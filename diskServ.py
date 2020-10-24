
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


