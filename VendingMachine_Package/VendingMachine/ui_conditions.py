import random
from machine_service import update_machine_state


def read_sensors():

    temp = round(random.uniform(0, 130), 2)
    hum = round(random.uniform(0, 100), 2)

    return temp, hum


def determine_state(temp):

    if temp < 32:
        return "TOO COLD"

    if 33 <= temp <= 80:
        return "NORMAL"

    if 81 <= temp <= 120:
        return "WARNING"

    return "CRITICAL"


def process_machine_state(temp, hum):

    state = determine_state(temp)

    update_machine_state(state, temp, hum)

    return state