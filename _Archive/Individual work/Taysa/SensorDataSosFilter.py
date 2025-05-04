from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
from machine import Timer

import array
import sys
import time
import gc

#### Constants

FREQUENCY_HZ = 250
WEIGHT_PARAM = 1/FREQUENCY_HZ
BUFFER_SIZE = 100
#THRESHOLD = 1500 # 1500 is an empirical threshold, needs to be verified in the device.
THRESHOLD_ON = 5000
THRESHOLD_OFF = 10000
MAX_HR_BUFFER_SIZE = 500


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
    
# --- Live SOS filter class ---

class LiveSosFilter:
    """Live implementation of digital filter with second-order sections."""
    def __init__(self, sos, limit=5000):
        self.sos = sos
        self.limit = limit      
        self.n_sections = len(sos)
        self.state = [[0]*2 for i in range(self.n_sections)]
       
    def process(self, x):
        """Filter incoming data with cascaded second-order sections."""
        for s in range(self.n_sections):
            b0, b1, b2, a0, a1, a2 = self.sos[s]            
            y = b0*x + self.state[s][0]
            y = max(y, -self.limit)
            y = min(y, +self.limit)
            self.state[s][0] = b1*x - a1*y + self.state[s][1]
            self.state[s][1] = b2*x - a2*y
            x = y 
        return y

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
    global buffer, finger_state, debounce_counter, last_detected_finger, hr_data_buffer, sosfilter
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
                hr_data_buffer.clear()
                gc.collect() #collect garbage
                print("Finger REMOVED!")
                
        else:
            debounce_counter = 0
    
        last_detected_finger = detected_finger  # Update last known
        buffer.clear()  # Clear buffer efficiently without reallocating
    
    #store HR data when finger is on
    if finger_state == FINGER_ON and len(hr_data_buffer) < MAX_HR_BUFFER_SIZE:
        value = data.read_u16()
        filtered_value = sosfilter.process(value)
        hr_data_buffer.append(filtered_value)

        #storage check
        if len(hr_data_buffer) % 500 == 0:
            print(f"Stored {len(hr_data_buffer)} HR samples so far...")
            
        
        #buffer = RoundRobin(BUFFER_SIZE)

# --- SOS coefficients for your pulse filter ---
sos = [
    [ 0.99375596, -0.99375596,  0.        ,  1.        , -0.98751193, 0.        ],
    [ 0.009477  , -0.01795636,  0.009477  ,  1.        , -1.87609963,  0.88074724],
    [ 1.        , -1.98153609,  1.        ,  1.        , -1.95391259,  0.95787597]
]

# --- Create the LiveSosFilter instance ---
sosfilter = LiveSosFilter(sos, 5000)
timer = Timer()
timer.init(mode=Timer.PERIODIC, freq=FREQUENCY_HZ, callback=timer_callback)

#keep main thread alive without wasting CPU
while True:
    time.sleep(1)


