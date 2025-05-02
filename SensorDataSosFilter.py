from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
from machine import Timer

from src.buffer import RoundRobin
from src.calculations import HRVAnalysis

import array
import sys
import time
import gc

#### Constants

DEBOUNCE_LIMIT = 3
WEIGHT_PARAM = 1/250
THRESHOLD_ON = 5000
THRESHOLD_OFF = 10000

##### Finger detection (FD)
FD_FREQUENCY_HZ = 250
FD_BUFFER_SIZE = 100

##### Heartrate calculation (HB)
HR_FREQUENCY_HZ = 1
HR_BUFFER_SIZE = FD_FREQUENCY_HZ * 5
    
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

data = ADC(Pin(26)) # Check if Pin(26) or Pin(27)

fd_buffer = RoundRobin(FD_BUFFER_SIZE)
hr_buffer = RoundRobin(HR_BUFFER_SIZE)

hrv = HRVAnalysis()

FINGER_ON = 1
FINGER_OFF = 0
finger_state = FINGER_OFF

#check the stability of the finger on the sensor to validate the state of the finger
debounce_counter = 0

last_detected_finger = False

#### Smooth average

def calculate_smooth_average(buffer):
    smoothed = array.array('d', [0]*len(buffer))
    for index in range(0, len(buffer)):
        smoothed[index] = (1-WEIGHT_PARAM)*smoothed[index-1] + WEIGHT_PARAM*buffer[index]
    return smoothed

#### Detect finger

def detect_finger(buffer):
    if len(buffer) < FD_BUFFER_SIZE:
        return None

    smoothed = calculate_smooth_average(buffer)
    avg_value = sum(smoothed) / len(smoothed)

    if avg_value > THRESHOLD_OFF:
        return False  # Finger OFF
    elif avg_value < THRESHOLD_ON:
        return True   # Finger ON
    else:
        return None   # Stay in current state

def hr_timer_callback(timer):
    global fd_buffer, finger_state, debounce_counter, last_detected_finger, hr_buffer, sosfilter

    print(f"Finger state: {finger_state}")

    #store HR data when finger is on
    if finger_state == FINGER_ON:
        if len(hr_buffer) == HR_BUFFER_SIZE:
            hr_samples = hr_buffer.get()
            #hr_samples = calculate_smooth_average(hr_samples)
            #hr_samples_filtered = array.array('f', [0] * len(hr_samples))
            hr_samples_filtered = []
            for hr_sample in hr_samples:
                hr_samples_filtered.append(sosfilter.process(hr_sample))
            
            hrv.add_sample(hr_samples_filtered)
            hrv.calculate_mean_HR()
            print("Mean HR",hrv.meanHR_value)
            
        else:
            print("Collecting samples (5s) ...")

def fd_timer_callback(timer):
    global fd_buffer, finger_state, debounce_counter, last_detected_finger, hr_buffer, sosfilter
    raw_data = data.read_u16()    
    fd_buffer.append(raw_data)

    if finger_state == FINGER_ON:
        hr_buffer.append(raw_data)

    if len(fd_buffer) == FD_BUFFER_SIZE:
        fd_samples = fd_buffer.get()
        detected_finger = detect_finger(fd_samples)

        if detected_finger is None:
            detected_finger = last_detected_finger  # HOLD the last detection
      
        if detected_finger and finger_state == FINGER_OFF:
            debounce_counter += 1
            if debounce_counter >= DEBOUNCE_LIMIT:
                finger_state = FINGER_ON
                debounce_counter = 0

        elif not detected_finger and finger_state == FINGER_ON:
            debounce_counter += 1
            if debounce_counter >= DEBOUNCE_LIMIT:
                finger_state = FINGER_OFF
                debounce_counter = 0
                hr_buffer.clear()
                gc.collect() #collect garbage
                
        else:
            debounce_counter = 0
    
        last_detected_finger = detected_finger  # Update last known
        fd_buffer.clear()  # Clear buffer efficiently without reallocating

# --- SOS coefficients for your pulse filter ---
sos = [
    [ 0.99375596, -0.99375596,  0.        ,  1.        , -0.98751193, 0.        ],
    [ 0.009477  , -0.01795636,  0.009477  ,  1.        , -1.87609963,  0.88074724],
    [ 1.        , -1.98153609,  1.        ,  1.        , -1.95391259,  0.95787597]
]

# --- Create the LiveSosFilter instance ---
sosfilter = LiveSosFilter(sos, HR_BUFFER_SIZE)

fd_timer = Timer()
fd_timer.init(mode=Timer.PERIODIC, freq=FD_FREQUENCY_HZ, callback=fd_timer_callback)

hr_timer = Timer()
hr_timer.init(mode=Timer.PERIODIC, freq=HR_FREQUENCY_HZ, callback=hr_timer_callback)

#keep main thread alive without wasting CPU
while True:
    time.sleep(1)