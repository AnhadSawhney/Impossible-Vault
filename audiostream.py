import sounddevice as sd
import numpy as np
import threading

def get_last_vol(stream):
    print(max(stream.latest_vol))
    return max(stream.latest_vol)

# create a new thread that will run real time audio stream
class StreamT(threading.Thread):
    def __init__(self, threshold):
        threading.Thread.__init__(self)
        self.stream = sd.Stream(callback=self.print_sound, samplerate=16000)
        self.latest_vol = [0]*5
        self.threshold = threshold

    def run(self):
        self.event = threading.Event()
        with self.stream:
            self.event.wait()

    def terminate(self):
        self.stream.abort()
        self.event.set()


    # saves current volume norm to mic_level var
    def print_sound(self, indata, outdata, frames, time, status):
        volume_norm = (np.linalg.norm(indata)*10)**.5
        self.latest_vol =  self.latest_vol[1:] + [volume_norm]
        #print(get_last_vol(self), self.latest_vol[-1])

        if volume_norm > self.threshold:
            print("Volume exceeded:", volume_norm)
            if self.is_alive():
                self.terminate()
                self.join()
        #print ("|" * int(volume_norm))
'''
def end_stream():
    if stream_thread.is_alive():
        stream_thread.terminate()
        stream_thread.join()
        '''

#streamthread = StreamT(25)
#streamthread.start()