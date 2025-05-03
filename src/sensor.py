###Sensor's performance###

from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from filefifo import Filefifo
from machine import Timer
from src.buffer import RoundRobin
from src.calculations import HRVAnalysis
import array, asyncio, time,gc

#-----------------------Initialise variables---------------------


FINGER_ON = 1
FINGER_OFF = 0
finger_state = FINGER_OFF

#check the stability of the finger on the sensor to validate the state of the finger
debounce_counter = 0
DEBOUNCE_LIMIT = 3
last_detected_finger = False


#### Constants
FREQUENCY_HZ = 250
WEIGHT_PARAM = 1/FREQUENCY_HZ
BUFFER_SIZE = 100
THRESHOLD_ON = 5000
THRESHOLD_OFF = 10000

sensor = ADC(Pin(26))
buffer = RoundRobin(BUFFER_SIZE)
fifo = Fifo(3000)
hr_data_buffer = []  # Store HR signal when finger detected4
hrv = HRVAnalysis()
sample_list = []
first_window = True
to_draw = []
window_min = None
window_max = None
fin_draw = []
start_index = 0

i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
#-----------------------Buffer handling---------------------
def timer_callback(timer):
    global buffer, finger_state, debounce_counter, last_detected_finger
    data = sensor.read_u16()
    buffer.append(data)
    if finger_state == FINGER_ON:
        fifo.put(data)
    
def get_buffer(buffer):
    return buffer.get()
    
def get_fifo():
    global fifo
    return fifo.get()

#-----------------------Logic for finger detection---------------------


def calculate_smooth_average(buffer):
    smoothed = array.array('d', [0]*len(buffer))
    for index in range(1, len(buffer)):
        smoothed[index] = (1-WEIGHT_PARAM)*smoothed[index-1] + WEIGHT_PARAM*buffer[index]
    return smoothed

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

#--------------Save data-----------------------------------
def save_data(data):
    filename = "raw_data.txt"
    try:
        with open(filename, "a") as f:
            f.write(str(data) + "\n")
    except OSError as e:
        print(f"Error appending to file '{filename}': {e}")
        
def clear_data():
    filename = "raw_data.txt"
    try:
        with open(filename, "w") as f:
            pass  
        print(f"File '{filename}' has been cleared.")
    except OSError as e:
        print(f"Error clearing file '{filename}': {e}")
        
#-----------------------Data handling---------------------
async def data_handling():
    global sample_list
    while True:
        if fifo.has_data():
            #print("Start")
            while fifo.has_data():
                value = fifo.get()
                sample_list.append(value)
             
            #Handle data
            if len(sample_list) >= 500:
                to_draw.append(sample_list[:500])
                hrv.add_sample(sample_list[:500])
                hrv.calculate_mean_HR()
                print("Mean HR",hrv.meanHR_value)
                sample_list = sample_list[500:]
            
        await asyncio.sleep(0.05)   

def scale(samples):
    global first_window, window_min, window_max
    #Scale value
    if first_window:
        window_min = min(samples[:250])
        window_max = max(samples[:250])
        first_window = False
    scl_range = window_max - window_min
    temp_ls = []
    for sample in samples:
        value = ((sample - window_min)/scl_range) * 50
        temp_ls.append(value)
    for i in range(0,501,5):
        fin_draw.append(sum(temp_ls[i:i+5])/5)
        
async def draw():
    global fin_draw, start_index, to_draw
    while True:
        if len(to_draw) >= 500:
            print("Draw")
            scale(to_draw)
            oled.fill(0)
            x1 = 0
            y1 = 0
            if len(fin_draw) >= 128:
                for y in fin_draw[start_index:]:
                    x2 = x1 +1
                    y2 = y
                    oled.line(x1,y1, x2,y2,1)
                    x1 = x2
                    y1 = y2
                    if x1 > 127:
                        break
                oled.show()
        start_index += 1
        asyncio.sleep(0.05)
                
def check_finger():
    global buffer, finger_state, debounce_counter, last_detected_finger
    if len(buffer) == BUFFER_SIZE:
        samples = get_buffer(buffer)
        detected_finger = detect_finger(samples)
        
        if detected_finger is None:
            detected_finger = last_detected_finger  # HOLD the last detection

        #print(f"detect_finger: {detected_finger}")
        
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
async def main():
    timer = Timer()
    timer.init(mode=Timer.PERIODIC, freq=FREQUENCY_HZ, callback=timer_callback)
    asyncio.create_task(data_handling())
    #asyncio.create_task(draw())
    while True:
        gc.collect()
        check_finger()
        await asyncio.sleep(0.05)
        
        

"""
asyncio.run(main())"""