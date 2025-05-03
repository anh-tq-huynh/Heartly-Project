from fifo import Fifo
from piotimer import Piotimer
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import micropython,time

micropython.alloc_emergency_exception_buf(200)

debounce_delay = 500
last_pressed = time.ticks_ms()

class Sensor:
    def __init__(self):
        self.adc = ADC(Pin(26, Pin.IN))
        self.signal_fifo = Fifo(size=50, typecode='i')
        self.collecting = False

    def start_collect(self, tmr):
        if self.collecting:
            self.tmr = Piotimer(freq=250, callback=self.sensor_handler)
    
    def stop_collect(self):
        self.tmr.deinit()
        self.colelcting = False
        
    def sensor_handler(self):
        if self.collecting:
            self.adc_fifo.put(self.adc.read_u16())
            
class Display:
    def __init__(self):
        self.i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
        self.oled_width = 128
        self.oled_height = 64
        self.oled = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
    def show(self):
        self.oled.show()
        
    def clear(self):
        self.oled.fill(0)
        
    def run(self,function):
        function()
        self.show()
        
class Encoder:
    def __init__(self):
        self.a = Pin(10, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(11, mode = Pin.IN, pull = Pin.PULL_UP)
        self.push = Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)
        self.a.irq(handler = self.rotation, trigger = Pin.IRQ_RISING, hard = True)
        self.push.irq(handler = self.button_pushed, trigger = Pin.IRQ_FALLING, hard = False)
        self.fifo = Fifo(30, "i")
        self.row = 1
        
        
    def rotation(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
            
    
    def button_pushed(self,pin):
        global debounce_delay, last_pressed
        if self.push.value() == 0:
            pressed_time = time.ticks_ms()
            if time.ticks_diff(pressed_time, last_pressed) > debounce_delay:
                self.fifo.put(2)
                last_pressed = pressed_time
