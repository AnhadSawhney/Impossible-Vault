import codegen
import time

keythread = codegen.keyT(codegen.keys, True)
keythread.start()

input()
keythread.stop_looping()
keythread.join()

print("Done")
