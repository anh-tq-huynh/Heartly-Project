import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

color = 1

oled.fill(0)
oled.text('22.05.2025', 0, 0)
oled.text('14:46', 86, 0)
oled.text('Mean HR: 75',0 , 10)
oled.text('Mean PPI: 750', 0, 20)
oled.text('RMSSD: 23', 0, 30)
oled.text('SDNN: 22', 0, 40)
oled.text('SNS: 1.234', 0, 50)
oled.text('PNS: -1.234', 0, 60)
oled.show()