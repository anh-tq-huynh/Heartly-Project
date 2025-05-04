import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Setup button (for future use)
button = Pin(12, Pin.IN, Pin.PULL_UP)

def scroll_text_horizontally(text, repeat=3, speed=0):
    for i in range(repeat):
        for i in range(len(text) * 8):  # 8 pixels per character
            oled.fill(0)
            oled.text(text, -i + oled_width, 28)  # 28 is vertical center
            oled.show()
            time.sleep(speed)
    return

def error():
    message = "Error: Unable to send data. Press button to retry or wait 30 sec"
    scroll_text_horizontally(message, repeat=3)
    return

error()