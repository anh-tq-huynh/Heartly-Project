###CODE TO DRAW LIVE DATA###

from piotimer import Piotimer
from machine import Pin, ADC,I2C
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import time,micropython

micropython.alloc_emergency_exception_buf(200)

class SensorReader:
    def __init__(self):
        self.adc = ADC(Pin(26))
        self.signal_fifo = Fifo(1000)
    
    def callback_handler(self, timer):
        self.signal_fifo.put(self.adc.read_u16())
        
class DataHandling:
    def __init__(self):
        self.ppi = []
        self.prev_peak = 0
        self.prev_peak_ms = 0
        self.current_peak = 0
        self.current_peak_ms = 0
        self.mean_hr = None
        self.hr = None
        
    def find_threshold(self, raw_data):
        if len(raw_data) >= 500:
            minimum = min(raw_data[-500:])
            maximum = max(raw_data[-500:])
            threshold = (minimum + maximum)/ 2
            return threshold, minimum, maximum
        
    def find_peak(self, current_value, current_time,data_list):
        threshold_data = self.find_threshold(data_list)
        if threshold_data != None:
            threshold,minimum, maximum = threshold_data
            if current_value > threshold:
                self.current_peak = current_value
                self.current_peak_ms = current_time
                    
            else:
                if self.current_peak !=0:
                    if self.prev_peak_ms != 0:
                        ppi = self.current_peak_ms - self.prev_peak_ms
                        if 400 <= ppi <= 2000:
                            self.ppi.append(ppi+300)
                            #print("Add PPi")
                            if len(self.ppi) >= 500:
                                self.ppi.pop(0)
                    self.prev_peak = self.current_peak
                    self.prev_peak_ms = self.current_peak_ms
                    
                self.current_peak = 0
                self.current_peak_ms = 0
                    
                
sensor = SensorReader()
tmr = Piotimer(mode = Piotimer.PERIODIC, freq = 250, callback = sensor.callback_handler)

#initiate reading data and oled
i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


handling = DataHandling()
recorded_time = 0
data_list = []
count = 0
def draw_data(oled, data_list):
#     while sensor.signal_fifo.has_data():
#         value = sensor.signal_fifo.get() >> 6
#         data_list.append(value)
        recorded_time += 25 #ms
        handling.find_peak(value,recorded_time,data_list)
        #print(handling.ppi)
        
        if len(data_list) >= 128:
            oled.fill(0)
            prev_x = 0
            prev_y = 0
            scale_list = data_list[count:count + 128]
            min_scl = min(scale_list)
            max_scl = max(scale_list)
            scl_range = max_scl - min_scl
            oled.text("Mean HR: 80 BPM", 0, 46,1)
            for x in range(128):
                if scl_range > 0:
                    y = int(((scale_list[x] - min_scl) / scl_range) * 40)
                else:
                    y = height // 2

                if x > 0:
                    oled.line(prev_x, 40 - 1 - prev_y, x, 40 - 1 - y, 1)

                prev_x = x
                prev_y = y
            x = 0
            count += 1
            if recorded_time >= 5000:
                oled.text("PRESS to stop",0,56,1)
            oled.show()
        if len(data_list) >= 1250:
            data_list = data_list [1250:]
        time.sleep(0.05)
        
        """
        print(len(handling.ppi))
        if recorded_time % 5000 and len(handling.ppi) >= 20:
            hr = 60*((sum(handling.ppi[:])/ len(handling.ppi))/1000)
            print("Heart rate", hr)"""
