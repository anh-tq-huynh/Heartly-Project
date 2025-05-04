from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
from machine import Timer
from calculations import HRVAnalysis
import array
import sys
import time

#### Constants

FREQUENCY_HZ = 250
WEIGHT_PARAM = 1/FREQUENCY_HZ
BUFFER_SIZE = 100
#THRESHOLD = 1500 # 1500 is an empirical threshold, needs to be verified in the device.
THRESHOLD_ON = 5000
THRESHOLD_OFF = 10000


#### Round Robin

# Improvement: consider adding a 

class RoundRobin:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.is_full = False

    def append(self, item):
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.size

        if self.is_full:
            self.tail = (self.tail + 1) % self.size

        if self.head == self.tail:
            self.is_full = True

    def get(self):
        if not self.is_full and self.head == self.tail:
            return []  # buffer is empty

        items = []
        idx = self.tail

        while True:
            items.append(self.buffer[idx])
            if idx == self.head - 1 and not (self.is_full and self.head == self.tail):
                break
            idx = (idx + 1) % self.size
            if idx == self.tail:
                break

        return items
    
    def clear(self):
        self.head = 0
        self.is_full = False
        
    def __len__(self):
        if self.is_full:
            return self.size
        if self.head >= self.tail:
            return self.head - self.tail
        return self.size + self.head - self.tail
    
#### Timer callback

# Check if Pin(26) or Pin(27)

data = ADC(Pin(26))
buffer = RoundRobin(BUFFER_SIZE)
hr_data_buffer = []  # Store HR signal when finger detected

FINGER_ON = 1
FINGER_OFF = 0
finger_state = FINGER_OFF

#check the stability of the finger on the sensor to validate the state of the finger
debounce_counter = 0
DEBOUNCE_LIMIT = 3
last_detected_finger = False

#### Smooth average

def calculate_smooth_average(buffer):
    smoothed = array.array('d', [0]*len(buffer))
    for index in range(1, len(buffer)):
        smoothed[index] = (1-WEIGHT_PARAM)*smoothed[index-1] + WEIGHT_PARAM*buffer[index]
    return smoothed

#### Detect finger

#def detect_finger(buffer):
    # Avoid detection if buffer is not full
    #if len(buffer) < BUFFER_SIZE:
        #return False
    
    #smoothed = calculate_smooth_average(buffer)
    #for sample in smoothed:
        #if sample > THRESHOLD:
            #return False
    #return True

def detect_finger(buffer):
    if len(buffer) < BUFFER_SIZE:
        return None

    smoothed = calculate_smooth_average(buffer)
    avg_value = sum(smoothed) / len(smoothed)

    if avg_value > THRESHOLD_OFF:
        return False  # Finger OFF
    elif avg_value < THRESHOLD_ON:
        return True   # Finger ON
    else:
        return None   # Stay in current state



def timer_callback(timer):
    global buffer, finger_state, debounce_counter, last_detected_finger
    buffer.append(data.read_u16())
    
    if len(buffer) == BUFFER_SIZE:
        samples = buffer.get()
        detected_finger = detect_finger(samples)
        
        if detected_finger is None:
            detected_finger = last_detected_finger  # HOLD the last detection

        print(f"detect_finger: {detected_finger}")
        
        if detected_finger and finger_state == FINGER_OFF:
            debounce_counter += 1
            if debounce_counter >= DEBOUNCE_LIMIT:
                finger_state = FINGER_ON
                debounce_counter = 0
                print("Finger DETECTED!")
                
        elif not detected_finger and finger_state == FINGER_ON:
            debounce_counter += 1
            if debounce_counter >= DEBOUNCE_LIMIT:
                finger_state = FINGER_OFF
                debounce_counter = 0
                print("Finger REMOVED!")
                
        else:
            debounce_counter = 0
    
        last_detected_finger = detected_finger  # Update last known
        buffer.clear()  # Clear buffer efficiently without reallocating
    
    #store HR data when finger is on
    if finger_state == FINGER_ON:
        value = data.read_u16()
        hr_data_buffer.append(value)
        #storage check
        if len(hr_data_buffer) % 100 == 0:
            print(f"Stored {len(hr_data_buffer)} HR samples so far...")
            print(hr_data_buffer)
            hrv = HRVAnalysis()
            #samples = hrv.reading()
            peaks = hrv.find_peaks()
            ppi = hrv.calculate_ppi()
            mean_ppi = hrv.meanPPI()
            mean_hr = hrv.meanHR()
            sdnn = hrv.SDNN()
            rmssd = hrv.RMSSD()
            sdsd = hrv.SDSD()
            sd1 = hrv.SD1()
            sd2 = hrv.SD2()

            print('ppi=',mean_ppi)
            print('hr=',mean_hr)
            print('sdnn=',sdnn)
            print('rmssd',rmssd)
            print('sdsd=',sdsd)
            print('sd1=',sd1)

            
        
        #buffer = RoundRobin(BUFFER_SIZE)

timer = Timer()
timer.init(mode=Timer.PERIODIC, freq=FREQUENCY_HZ, callback=timer_callback)

#keep main thread alive without wasting CPU
while True:
    time.sleep(1)
