###CODE TO DRAW LIVE DATA###

from piotimer import Piotimer
from machine import Pin, ADC,I2C
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import time,micropython
import array



#handling = DataHandling()
data_list = []
count = 0
def draw_data(oled, data_list, hr,recorded_time, time_to_record):
#     while sensor.signal_fifo.has_data():
#         value = sensor.signal_fifo.get() >> 6
#         data_list.append(value)
#         handling.find_peak(value,recorded_time,data_list)
    #print(handling.ppi)
    
    if len(data_list) >= 128 * 5: # Using a value relevant to the drawing width
        oled.fill(0)
        prev_x = 0
        prev_y = 0

        # Ensure we don't go out of bounds of the array
        start_index = max(0, len(data_list) - 128 * 5)
        scale_list = data_list[start_index:] # Take the last 128 * 5 elements

        display_length = min(128, len(scale_list) // 5) if len(scale_list) >= 5 else len(scale_list)
        if display_length > 0:
            new_list = array.array('f') # Initialize an empty array of floats
            for i in range(display_length):
                start_index = i * 5
                end_index = (i + 1) * 5
                chunk = scale_list[start_index:end_index]

                if len(chunk) > 0:
                    average = sum(chunk) / len(chunk)
                    new_list.append(average)
                else:
                    new_list.append(0.0)

            min_scl = min(new_list)
            max_scl = max(new_list)
            scl_range = max_scl - min_scl
            text = f"Mean HR: {int(hr)} BPM"
            oled.text(text, 0, 46, 1)

            for x in range(display_length):
                if scl_range > 0:
                    y = int(((new_list[x] - min_scl) / scl_range) * 40)
                else:
                    y = 10

                if x > 0:
                    oled.line(prev_x, 40 - 1 - prev_y, x, 40 - 1 - y, 1)

                prev_x = x
                prev_y = y

        if recorded_time >= time_to_record:
            oled.text("PRESS to stop", 0, 56, 1)
        
        oled.show()
#         if len(data_list) >= 1250:
#             data_list = data_list [1250:]
#         time.sleep(0.05)
        


