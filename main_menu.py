from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import time

class Encoder:
    def __init__(self, rot_a, rot_b, rot_push):
        self.a = Pin(rot_a, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(rot_b, mode = Pin.IN, pull = Pin.PULL_UP)
        self.push = Pin(rot_push, mode = Pin.IN, pull = Pin.PULL_UP)
        self.fifo = Fifo(30, typecode = 'i')
        self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
        
    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)    
            
rotary = Encoder(10, 11, 12)

word_option0 = "HR"
word_option1 = "HRV Analysis"
word_option2 = "KUBIOS"
word_option3 = "HISTORY"

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

oled_width = 128
oled_height = 64
line_height = 9

oled = SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)

# Rotary range: [0,1,2,3]
step = 1
value = 0
max_value = 3

button_pressed = False

def update_menu_option(index, option_text):
    
    if value == index:
        word = f"[ {option_text} ]"
    else:
        word = f"  {option_text}  "
    oled.text(word, 0, line_height * index, 1)

    

def update_menu():
    global value, word_option0, word_option1, word_option2, word_option3
    oled.fill(0)
    for i, option in enumerate([word_option0, word_option1, word_option2, word_option3]):
        update_menu_option(i, option)
    oled.show()
    
   
update_menu()

while True:
    rotary_pushed = rotary.push()
    time.sleep(0.01)
    
    # Push button logic: state goes to 0 when pressed, and back to 1 when released.
    if rotary_pushed == 0:
        button_pressed = True
    elif button_pressed == True:
        button_pressed = False
        # Toggle led value according to the rotary value.
        if value == 0:
            oled.fill(0)
            wait_message = "30s to go..."
            oled.text(wait_message, 24, 32, 1)
            oled.show()
        elif value == 1:
            oled.fill(0)
            wait_message = "30s to go..."
            oled.text(wait_message, 24, 32, 1)
            oled.show()
        elif value == 2:
            oled.fill(0)
            wait_message = "30s to go..."
            oled.text(wait_message, 24, 32, 1)
            oled.show()
        elif value == 3:
            oled.fill(0)
            wait_message = "30s to go..."
            oled.text(wait_message, 24, 32, 1)
            oled.show()
        #update_menu()

    # Direction: 1 means clockwise, -1 means counter-clockwise.
    while rotary.fifo.has_data():
        direction = rotary.fifo.get()
        # Clockwise (incremental)
        if direction == 1:
            if value + step > max_value:
                value = max_value
            else:
                value += step
        # Counter-clockwise (decremental)
        else:
            if value - step < 0:
                value = 0
            else:
                value -= step
        update_menu()
