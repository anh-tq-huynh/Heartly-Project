import time
from machine import Pin, I2C, Timer
class History():
    def __init__(self):
        self.latest_max_rows=[]
        self.measurement_no=[]
        
    def measurements(self):
        latest_max_row=f"select measurement from history order by desc() limit 8 "
        return self.latest_max_row[:8]
        
    def measurement_data(self,measurement_no):
        measurement_no= f"select * from history where latest_max_row.measurement_no= {self.measurement_no} "
        return self.measurement_no

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
y=0
measurements=History.measurements()
while True:
    button.off()
    oled.text(measurements, 0, y, 1)
    oled.show()
    y=y+8
    time.sleep(0.05)
else:
        oled.fill(0)
        oled.show()
        time.sleep(0.05)