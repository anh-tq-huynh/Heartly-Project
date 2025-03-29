import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

text = "Sending data"
dot = "."
dot_start = 12*8
y = int(64/2)
oled.text(text,0,y,1)
oled.show()
show = 1
while True:
    for i in range(0,3):
        time.sleep(0.5)
        oled.text(dot, dot_start + i*8,y, 1)
        oled.show()
    oled.text(dot, dot_start,y, 0)
    oled.text(dot, dot_start + 8,y, 0)
    oled.text(dot, dot_start + 16,y, 0)
    time.sleep(0.5)
    oled.show()
