import sounddevice as sd
import numpy as np
import threading

# create a new thread that will run real time audio stream
class StreamT(threading.Thread):
    def __init__(self, threshold, event):
        threading.Thread.__init__(self)
        device_info = sd.query_devices()
        print(device_info)
        i = len(device_info)-1
        print("Choosing "+str(i))
        device_info = sd.query_devices(i, "input")
        sr = int(device_info['default_samplerate'])
        self.stream = sd.InputStream(device = i, callback=self.print_sound, samplerate=sr)
        self.latest_vol = [0]*3
        self.threshold = threshold
        self.event = event

    def run(self):
        with self.stream:
            self.event.wait()
        self.stream.abort()        

    def get_last_vol(self):
        #print(max(stream.latest_vol))
        #return max(self.latest_vol)
        if len(self.latest_vol) == 0:
            return 0
        return sum(self.latest_vol)/len(self.latest_vol)

    # saves current volume norm to mic_level var
    def print_sound(self, indata, frames, time, status):
        volume_norm = (np.linalg.norm(indata)*10)**.75
        self.latest_vol =  self.latest_vol[1:] + [volume_norm]
        #print(self.get_last_vol())

        if volume_norm > self.threshold:
            print("Volume exceeded:", volume_norm)
            #if self.is_alive():
            #    self.terminate()
            #    self.join()
        #print ("|" * int(volume_norm))
'''
def end_stream():
    if stream_thread.is_alive():
        stream_thread.terminate()
        stream_thread.join()
        '''

#streamthread = StreamT(25)
#streamthread.start()