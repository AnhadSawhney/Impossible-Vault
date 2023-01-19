import random
import string
import time
import threading
import os

KEYDELAY = 10


def generate_keys(n):
    out = []
    for i in range(n):
        out.append("".join(random.choices(string.ascii_uppercase, k=6)))

    return out


# print(generate_keys(20))

keys = [
    "DDNTBW",
    "TYCCGJ",
    "STFGDF",
    "EFWTEF",
    "VJGIIF",
    "LURHBR",
    "LYTGUB",
    "QBFLHC",
    "WXDMOF",
    "DOVFQL",
    "YLEZKW",
    "BHRMNG",
    "TSQFVW",
    "JAHDIF",
    "KSAXXT",
    "CKAFAD",
    "RPPFOQ",
    "RRDLQR",
    "DJIJBV",
    "YIQRAT",
]

# create a new thread that will choose a new key every 3 seconds
class keyT(threading.Thread):
    def __init__(self, keys, p):
        threading.Thread.__init__(self)
        self.keep_looping = True
        self.keys = keys
        self.k = keys[0]
        self.p = p
        print("Current key: " + self.k)

    def run(self):
        while self.keep_looping:
            s = time.localtime().tm_sec
            if s % KEYDELAY == 0:
                self.k = self.keys[s // KEYDELAY]
            if self.p:
                os.system("cls" if os.name == "nt" else "clear")
                print("Current key: " + self.k)
                left = KEYDELAY - s % KEYDELAY
                print("New key in: " + str(left) + " second", end="")
                print("s" if left != 1 else "")

            time.sleep(1)

    def stop_looping(self):
        self.keep_looping = False
