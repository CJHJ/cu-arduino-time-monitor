from flask import Flask, jsonify
from flask import g
from templates import app

from pymemcache.client import base
import sqlite3 as sql

import serial

import time
from multiprocessing import Process, Value


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Loop function to get newest sensor value
# Run by multiprocessing parallel to the server
def record_loop(loop_on):
    # Arduino config files
    output_file = 'timer_output.log'  # LOGFILE NAME
    connected = False
    baud_rate = 9600
    # CHANGE THIS TO YOUR ARDUINO SERIAL PORT
    locations = ['/dev/cu.usbmodem1422401']

    # Connect to sqlite
    # CHANGE THIS TO CONNECT TO YOUR SQLITE3 DB
    con = sql.connect('ranking.db')
    con.row_factory = dict_factory

    # Connect to memcached
    # CHANGE THIS TO YOUR CORRESPONDING MEMCACHED
    cache = base.Client(('localhost', 11211))

    # Variables
    is_watching = cache.get('is_watching')
    if not None:
        is_watching = int(is_watching.decode('utf-8'))
    else:
        cache.set('is_watching', 0)
        is_watching = int(cache.get('is_watching').decode('utf-8'))
    print("Is watching: {}".format(is_watching))

    current_team = cache.get('current_team')
    if not None:
        current_team = int(current_team.decode('utf-8'))
    else:
        cache.set('current_team', 0)
        current_team = int(cache.get('current_team').decode('utf-8'))
    print("Current team: {}".format(current_team))

    # Check for connection
    for device in locations:
        try:
            print("Connecting to {}...".format(device))
            serial_device = serial.Serial(device, baud_rate)
            break
        except:
            print("Failed to connect to {}".format(device))

    while not connected:
        serial_in = serial_device.read()
        connected = True

    # If succeed
    if connected:
        with open(output_file, 'wb') as f:
            temp_string = []

            while loop_on.value == True:
                current_team = int(cache.get('current_team').decode('utf-8'))
                is_watching = int(cache.get('is_watching').decode('utf-8'))

                if serial_device.inWaiting():
                    x = serial_device.read()
                    temp_string.append(x)

                    if x == b'\n':
                        joined_string = b"".join(temp_string)
                        f.write(joined_string)

                        current_time = joined_string.decode(
                            'utf-8').rstrip('ms\r\n').split('s')
                        print("Is watching: {}".format(is_watching))
                        print("Current team: {}".format(current_team))
                        print("Measured time: {}".format(
                            current_time))

                        if is_watching and current_time[0] != '':
                            current_time = float(
                                current_time[0] + '.' + current_time[1])
                            print("Insert into db")
                            cur = con.cursor()
                            cur.execute("insert into time_history(id, time) values ({}, {})".format(
                                current_team, current_time))

                            con.commit()

                        # Get best time
                        cur = con.cursor()
                        cur.execute(
                            "select * from time_history where id = {} order by cast(time as float) asc".format(current_team))
                        time_history = cur.fetchall()

                        if is_watching and len(time_history) != 0:
                            print("Best time: {}".format(time_history[0]))
                            best_time = time_history[0]['time']

                            cur = con.cursor()
                            cur.execute("update middle_score set time = {} where id = {}".format(
                                best_time, current_team))

                            con.commit()
                            print("Updated!")

                        temp_string = []

                    f.flush()

            serial_device.close()


if __name__ == '__main__':
    recording_on = Value('b', True)
    p = Process(target=record_loop, args=(recording_on,))
    p.start()
    app.config.from_object('configurations.DevelopmentConfig')
    app.run(use_reloader=False)
    p.join()
