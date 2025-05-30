###READ AND PROCESS DATA FROM SENSOR###
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
from machine import Timer

from src.buffer import RoundRobin
from src.calculations import HRVAnalysis
from src.graphing import draw_data

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
    smoothed = array.array('H', [0]*len(buffer))
    for index in range(0, len(buffer)):
        smoothed[index] = int((1-WEIGHT_PARAM)*smoothed[index-1] + WEIGHT_PARAM*buffer[index])
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

def update_finger_state():
    global fd_buffer, hr_buffer, finger_state, debounce_counter, last_detected_finger

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
                
        else:
            debounce_counter = 0
    
        last_detected_finger = detected_finger  # Update last known
        #fd_buffer.clear()  # Clear buffer efficiently without reallocating

# --- SOS coefficients for your pulse filter ---

# -- OLD: Using 0.5 Hz (2000ms PPI ~ 30 BPM) to 5.0 Hz (200ms PPI ~ 300 BPM)
#sos = [
#    [ 0.99375596, -0.99375596,  0.        ,  1.        , -0.98751193,  0.        ],
#    [ 0.009477  , -0.01795636,  0.009477  ,  1.        , -1.87609963,  0.88074724],
#    [ 1.        , -1.98153609,  1.        ,  1.        , -1.95391259,  0.95787597]
#]

# -- NEW: Using 0.5 Hz (2000ms PPI ~ 30 BPM) to 3.3 Hz (300ms PPI ~ 200 BPM)
sos = [
    [ 0.99375596, -0.99375596,  0.        ,  1.        , -0.98751193,  0.        ],
    [ 0.00958516, -0.01872483,  0.00958516,  1.        , -1.91760327,  0.91966803],
    [ 1.        , -1.99194807,  1.        ,  1.        , -1.97026504,  0.97200235]
]

# --- Create the LiveSosFilter instance ---
sosfilter = LiveSosFilter(sos, HR_BUFFER_SIZE)

# --- Finger detection timer ---

def fd_timer_callback(timer):
    global fd_buffer, hr_buffer, finger_state
    raw_data = data.read_u16()    
    fd_buffer.append(raw_data)

    if finger_state == FINGER_ON:
        hr_buffer.append(raw_data)



# ---- Main loop ----
# i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
# oled_width = 128
# oled_height = 64
# oled = SSD1306_I2C(oled_width, oled_height, i2c)

def finger_sensor(time_to_record,oled,encoder):
    global countdown_done, finger_state
    fd_timer = Timer()
    fd_timer.init(mode=Timer.PERIODIC, freq=FD_FREQUENCY_HZ, callback=fd_timer_callback)
    recorded_time = 0
    hrv.reset()

    prev_hr_samples = array.array('H', [0]*128)

    while True:
            
        #Check if any input is added to the encoder
        if encoder.fifo.has_data() and recorded_time > time_to_record:
            direction = encoder.fifo.get()
            if direction == 2:
                fd_buffer.clear()
                hr_buffer.clear()
                fd_timer.deinit()
                finger_state = FINGER_OFF
                return hrv
            
        # Check if finger detection buffer (100 samples) is full to update finger state.
        if len(fd_buffer) == FD_BUFFER_SIZE:
            update_finger_state()
            print (finger_state)

        # Check if finger is pressed and the heartrate buffer is full to calculate heartrate data.
        if finger_state == FINGER_ON:    
#             graph_timer = Timer()
#             graph_timer.init(mode=Timer.PERIODIC, freq=1000, callback=lambda t: draw_timer_callback(t, oled, hrv, recorded_time, time_to_record))
            if len(hr_buffer) == HR_BUFFER_SIZE:
                recorded_time += 5000 #ms
#                 if recorded_time >= time_to_record:
#                     oled.text("PRESS to stop",0,56,1)
                    
      
                hr_samples = hr_buffer.get()
                print(f"hr_samples: {len(hr_samples)}")
                
                prev_hr_samples = array.array('H', [0]*len(hr_samples))
                for index in range(len(hr_samples)):
                    prev_hr_samples[index] = hr_samples[index]
                    
                    
                draw_data(oled,prev_hr_samples,hrv.meanHR_value, recorded_time, time_to_record)
                del prev_hr_samples
                
                gc.collect()

                hr_samples_filtered = array.array('d', [0] * len(hr_samples))
                for index in range(len(hr_samples)):
                    hr_samples_filtered[index] = sosfilter.process(hr_samples[index])
                hrv.add_sample(hr_samples_filtered)
                del hr_samples_filtered
                hrv.calculate_all()
#                 print(len(hrv.PPIs))
#                 print(f"peaks: {hrv.peaks} ppis: {hrv.PPIs}")
#                 print(f"mean ppi: {hrv.meanPPI_value}")
#                 print(f"mean hr: {hrv.meanHR_value}")
                
#                 if len(prev_hr_samples) >= 1250:
#                     prev_hr_samples = [1250:]
                
                
            else:
                for i in range(5,0,-1):
                    oled.fill(0)
                    print(f"Collecting samples (5s)...")
                    oled.text("Collecting data",5,20,1)
                    oled.text(f"{i} seconds left",5,40,1)
                    time.sleep(1)
                    oled.show()
                countdown_done = True
                
        else:
            print("Waiting for finger...")
            oled.fill(0)
            oled.text("Place your",10,10,1)
            oled.text("index finger",10,20,1)
            oled.text("on the sensor",10,30,1)
            oled.show()

        time.sleep(0.05)

