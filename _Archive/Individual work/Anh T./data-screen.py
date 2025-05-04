import time
import framebuf
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

mean_hr = 75
mean_ppi = 750
rmssd = 23
sns = 1.234
pns = -1.234

data = { "Mean HR" : 75,
         "Mean PPI": 750,
         "RMSSD": 23,
         "SNS": 1.234,
         "PNS": -1.234
         }
