#!/usr/bin/python
# -*- encoding: utf-8 -*-

# MAC address of HRM
# D4:EA:15:9F:4A:EE

"""
    BLEHeartRateLogger
    ~~~~~~~~~~~~~~~~~~~

    A tool to log your heart rate using a Bluetooth low-energy (BLE) heart rate
    monitor (HRM). The tool uses system commands (hcitool and gatttool) to
    connect to the BLE HRM and parses the output of the tools. Data is
    interpreted according to the Bluetooth specification for HRM and saved in a
    sqlite database for future processing. In case the connection with the BLE
    HRM is lost, connection is restablished.

    :copyright: (c) 2015 by fg1
    :license: BSD, see LICENSE for more details
"""

__version__ = "0.1.1"

import os
import sys
import time
import pexpect
import threading

def interpret(data):
    """
    data is a list of integers corresponding to readings from the BLE HR monitor
    """

    byte0 = data[0]
    res = {}
    res["hrv_uint8"] = (byte0 & 1) == 0
    sensor_contact = (byte0 >> 1) & 3
    if sensor_contact == 2:
        res["sensor_contact"] = "No contact detected"
    elif sensor_contact == 3:
        res["sensor_contact"] = "Contact detected"
    else:
        res["sensor_contact"] = "Sensor contact not supported"
    res["ee_status"] = ((byte0 >> 3) & 1) == 1
    res["rr_interval"] = ((byte0 >> 4) & 1) == 1

    if res["hrv_uint8"]:
        res["hr"] = data[1]
        i = 2
    else:
        res["hr"] = (data[2] << 8) | data[1]
        i = 3

    if res["ee_status"]:
        res["ee"] = (data[i + 1] << 8) | data[i]
        i += 2

    if res["rr_interval"]:
        res["rr"] = []
        while i < len(data):
            # Note: Need to divide the value by 1024 to get in seconds
            res["rr"].append((data[i + 1] << 8) | data[i])
            i += 2

    return res    

class HeartT(threading.Thread):
    def __init__(self, threshold, event):
        threading.Thread.__init__(self)
        self.latest_hr = [0]*3 # lifo buffer of last N readings
        self.threshold = threshold
        self.event = event
        self.res = None # latest hr data
        self.event = threading.Event()

    def run(self):
        debug_gatttool=False
        check_battery=False
        hr_handle=None
        addr = "D4:EA:15:9F:4A:EE"

        hr_ctl_handle = None
        retry = True
        gt = None
        while retry and not self.event.is_set():
            while not self.event.is_set():
                print("Establishing connection to " + addr)
                gt = pexpect.spawn("gatttool -b " + addr + " -t random --interactive")
                if debug_gatttool:
                    gt.logfile = sys.stdout

                gt.expect(r"\[LE\]>")
                gt.sendline("connect")

                try:
                    i = gt.expect(["Connection successful.", r"\[CON\]"], timeout=30)
                    if i == 0:
                        gt.expect(r"\[LE\]>", timeout=30)

                except pexpect.TIMEOUT:
                    print("Connection timeout. Retrying.")
                    continue

                except KeyboardInterrupt:
                    print("Received keyboard interrupt. Quitting cleanly.")
                    retry = False
                    break
                break

            if not retry:
                break

            print("Connected to " + addr)

            if check_battery:
                gt.sendline("char-read-uuid 00002a19-0000-1000-8000-00805f9b34fb")
                try:
                    gt.expect("value: ([0-9a-f]+)")
                    battery_level = gt.match.group(1)
                    print("Battery level: " + str(int(battery_level, 16)))

                except pexpect.TIMEOUT:
                    print("Couldn't read battery level.")

            if hr_handle == None:
                # We determine which handle we should read for getting the heart rate
                # measurement characteristic.
                gt.sendline("char-desc")

                while not self.event.is_set():
                    try:
                        gt.expect(r"handle: (0x[0-9a-f]+), uuid: ([0-9a-f]{8})", timeout=10)
                    except pexpect.TIMEOUT:
                        break
                    handle = gt.match.group(1).decode()
                    uuid = gt.match.group(2).decode()

                    if uuid == "00002902" and hr_handle:
                        hr_ctl_handle = handle
                        break

                    elif uuid == "00002a37":
                        hr_handle = handle

                if hr_handle == None:
                    print("Couldn't find the heart rate measurement handle?!")
                    return

            if hr_ctl_handle:
                # We send the request to get HRM notifications
                gt.sendline("char-write-req " + hr_ctl_handle + " 0100")

            # Time period between two measures. This will be updated automatically.
            period = 1.
            last_measure = time.time() - period
            hr_expect = "Notification handle = " + hr_handle + " value: ([0-9a-f ]+)"

            while not self.event.is_set(): # THIS IS THE REAL LOOP
                try:
                    gt.expect(hr_expect, timeout=10)

                except pexpect.TIMEOUT:
                    # If the timer expires, it means that we have lost the
                    # connection with the HR monitor
                    print("Connection lost with " + addr + ". Reconnecting.")
                    try:
                        gt.wait()
                    except:
                        pass
                    time.sleep(1)
                    break

                except KeyboardInterrupt:
                    print("Received keyboard interrupt. Quitting cleanly.")
                    retry = False
                    break

                # We measure here the time between two measures. As the sensor
                # sometimes sends a small burst, we have a simple low-pass filter
                # to smooth the measure.
                tmeasure = time.time()
                period = period + 1 / 16. * ((tmeasure - last_measure) - period)
                last_measure = tmeasure

                # Get data from gatttool
                datahex = gt.match.group(1).strip()
                data = map(lambda x: int(x, 16), datahex.split(b' '))
                self.res = interpret(list(data))

                print(self.res)

                # add the reading from res.hr to the lifo buffer
                self.latest_hr = self.latest_hr[1:] + [self.res["hr"]]

    # We quit close the BLE connection properly
        if gt is not None:
            gt.sendline("quit")
            try:
                gt.wait()
            except:
                pass
    
    def get_last_hr(self):
        # return the average of self.latest_hrs
        if len(self.latest_hr) == 0:
            return 0
        return sum(self.latest_hr)/len(self.latest_hr)

    # saves current volume norm to mic_level var
    def print_hr(self):
        if self.res is not None:
            print(self.res)
        else:
            print("No hr data to print")
        
        if self.get_last_hr() > self.threshold:
            print("Heart rate is above threshold")

if __name__ == "__main__": # launch the thread
    threshold = 0.1
    hr_thread = HeartT(threshold)
    hr_thread.start()
    while 1:
        hr_thread.print_hr()
        time.sleep(1)
