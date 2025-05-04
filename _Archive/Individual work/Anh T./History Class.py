import time
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

rot_a = Pin(11, Pin.IN, Pin.PULL_UP)
rot_b = Pin(10, Pin.IN, Pin.PULL_UP)
encoder_button = Pin(12, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# History class
class History():
    def __init__(self):
        self.latest_max_rows = []
        self.measurement_no = []

    def measurements(self):
        #latest_max_row=f"select measurement from history order by desc() limit 8 "
        self.latest_max_row = ["Measurement 1", "Measurement 2", "Measurement 3","Measurement 4", "Measurement 5"]
        return self.latest_max_row[:8]
    
#   def measurement_data(self,measurement_no):
#       measurement_no= f"select * from history where latest_max_row.measurement_no= {self.measurement_no} "
#       return self.measurement_no
#

history = History()
measurements = history.measurements()
selected_index = 0
last_rotary = rot_a.value()
last_button = encoder_button.value()
last_time = time.ticks_ms()

def menu():
    oled.fill(0)
    for i, item in enumerate(measurements):
        arrow = "->" if i == selected_index else "  "
        oled.text(f"{arrow}{item}", 0, i * 8)
    oled.show()

menu()

while True:
    current_rot = rot_a.value()
    if current_rot != last_rotary:
        if rot_b.value() != current_rot:
            selected_index = (selected_index + 1) % len(measurements)
        else:
            selected_index = (selected_index - 1) % len(measurements)
        menu()
        last_rotary = current_rot
        time.sleep(0.05)

    current_button = encoder_button.value()
    if current_button == 0 and last_button == 1:
        #selected_index=history.measurement_data
        now = time.ticks_ms()
        if time.ticks_diff(now, last_time) > 200:  # debounce
            oled.fill(0)
            oled.text("Selected:", 0, 0)
            oled.text( measurements[selected_index], 0, 16)
            oled.show()
            time.sleep(1.5)
            menu()
            last_time = now
    last_button = current_button

    time.sleep(0.01)



#import time
#from ssd1306 import SSD1306_I2C
#from machine import Pin, I2C, Timer
#encoder=Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)
#i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
#oled_width = 128
#oled_height = 64
#oled = SSD1306_I2C(oled_width, oled_height, i2c)


#class History():
#    def __init__(self):
#        self.latest_max_rows=[]
#        self.measurement_no=[]
#        
#    def measurements(self):
#        #latest_max_row=f"select measurement from history order by desc() limit 8 "
#        self.latest_max_row=["Measurement 1","Measurement 2","Measurement 3","Measurement 4","Measurement 5"]
#        return self.latest_max_row[:8]
#        
#    def measurement_data(self,measurement_no):
#        #measurement_no= f"select * from history where latest_max_row.measurement_no= {self.measurement_no} "
#        return self.measurement_no
#
#
#history = History()
#measurements = history.measurements()
#oled.fill(0)
#y = 0
#for item in measurements:
#    oled.text(item, 0, y)
#    y += 8

#oled.show()

#while True:
#    time.sleep(0.5)