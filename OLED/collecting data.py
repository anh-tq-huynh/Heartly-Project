import time
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
x = 0
y = 20
color = 1

oled.fill(0)
oled.text('Collecting data...', x, y)
oled.show()
for i in range(30, 0, -1):
    oled.fill(0)
    oled.text('Collecting data...', x, y)
    oled.text(f'{i}s left', 30, 30)
    oled.show()
    time.sleep(1)

oled.fill(0)
oled.show()