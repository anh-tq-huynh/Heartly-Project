##FUNCTIONS FOR OLED DISPLAY##
from src.hardware import Display, Encoder
from src.Animations.waitingScreen import waiting_screen
from src.Animations.welcomingScreen import welcome
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import framebuf,time


class DisplayControl(Display):
    def __init__(self):
        super().__init__()
        self.rotary = Encoder()
        self.current_selection = 1
        self.state = None
        self.line_height = 9
        """
            self.state list:
            1 - Welcome screen
            2 - Establish WiFi and MQTT connection
            3 - Main menu
            4 - HR
            5 - HRV
            6 - Kubios
            7 - History
        """
    #------------------main actions--------------------------------------    
    def clear(self):
        super().clear()
        
    def show(self):
        super().show()
        
    def welcome(self):
        self.clear()
        welcome(self.oled)
        
    #------------------end screens--------------------------------------    
            
    def waiting_screen(self,text_input):
        self.clear()
        waiting_screen(text_input, self.oled)
        
    def connecting(self):
        self.waiting_screen("Connecting")
        
    def sending_data(self):
        self.waiting_screen("Sending data")
        
    def count_down(self):
        for i in range(10, 0, -1):
            self.oled.fill(0)
            self.oled.text(f"{i}s to go...", 24, 31, 1)
            self.oled.show()
            time.sleep(0.3)
            
    def print_text(self, text_input):
        self.clear()
        self.oled.text(text_input,0,32)
        self.show()
        
    def instruction_for_sensor(self):
        self.clear()
        self.oled.text("Please keep", 10,10,1)
        self.oled.text("your finger", 10,20,1)
        self.oled.text("for minimum", 10,30,1)
        self.oled.text("30s",10,40,1)
        self.show()
        
    def print_selected_history(self,history):
        color = 1
        self.clear()        
        self.oled.text(history["Time"], 0, self.line_height * 0)
        self.oled.text(f'Mean HR: {history["Mean HR"]}', 0, self.line_height * 1)
        self.oled.text(f'Mean PPI: {history["Mean PPI"]}', 0, self.line_height * 2)
        self.oled.text(f'RMSSD: {history["RMSSD"]}', 0, self.line_height * 3)
        self.oled.text(f'SDNN: {history["SDNN"]}', 0, self.line_height * 4)
        self.oled.text(f'PNS: {history["PNS"]}', 0, self.line_height * 5)
        self.oled.text(f'SNS: {history["SNS"]}', 0, self.line_height * 6)
 
        self.oled.show()
        
        
        while True:
            while self.rotary.fifo.has_data():
                direction = self.rotary.fifo.get()
                if direction == 2:
                    self.state = 3
                    return self.state
                
            time.sleep(0.05)
            
    def hr_collect(self):
        self.clear()
        self.oled.text("Place your",10,10,1)
        self.oled.text("index finger",10,20,1)
        self.oled.text("on the sensor",10,30,1)
        self.oled.text("PRESS to start",0,50,1)
        self.oled.show()
    
    def print_menu(self, options):
        bear = bytearray([0x1F, 0x61, 0x8B, 0xA2, 0xA2, 0x8B, 0x61, 0x1F])
        bear_framebuf = framebuf.FrameBuffer(bear, 8, 8, framebuf.MONO_VLSB)
        self.oled.fill(0)
        y_start = 12

        for index,option in enumerate(options):
            if index == self.current_selection -1:
                text = f"[ {option} ]"
            else:
                text = option
            self.oled.text(text,15, y_start,1)
            
            if self.current_selection == 1:
                self.oled.blit(bear_framebuf,5,12)
            else:
                self.oled.blit(bear_framebuf,5,(self.current_selection)*12)
            y_start += 12
        self.oled.show()
        
    def print_history(self, options, start_index):
        num_visible_lines = 6
        self.oled.fill(0)  
        bear = bytearray([0x1F, 0x61, 0x8B, 0xA2, 0xA2, 0x8B, 0x61, 0x1F])
        bear_framebuf = framebuf.FrameBuffer(bear, 8, 8, framebuf.MONO_VLSB)
        for i in range(start_index, min(start_index + num_visible_lines, len(options))):
            if i + 1 == self.current_selection:
                self.oled.text("[" + options[i] + "]", 25, (i - start_index) * 10)
                self.oled.blit(bear_framebuf,5,(i - start_index) * 10)# Highlight selected item
            else:
                self.oled.text("  " + options[i], 8, (i - start_index) * 10)
        self.oled.show()
            
    def execute_menu(self,options):
        self.print_menu(options)
        #print(self.rotary.fifo.has_data())
        while True:
            while self.rotary.fifo.has_data():
                direction = self.rotary.fifo.get()
                #print(direction)
                if direction == 1 and self.current_selection < len(options) :
                    self.current_selection += 1
                    self.print_menu(options)
                elif direction == -1 and self.current_selection > 1:
                    self.current_selection -= 1
                    self.print_menu(options)
                elif direction == 2:
                    self.state = self.current_selection + 3 #match the state with the options
                    print(self.state)
                    self.current_selection = 1
                    return self.state
    
    def execute_history(self,options):
        if options != []:
            start_index = 0
            num_visible_lines = 6
            self.print_history(options, start_index)
            
            while True:
                while self.rotary.fifo.has_data():
                    direction = self.rotary.fifo.get()
                    #print(direction)  # For debugging

                    if direction == 1:  # Rotary encoder clockwise
                        if self.current_selection < len(options):
                            self.current_selection += 1
                            if self.current_selection >= start_index + num_visible_lines:
                                start_index += 1  # Scroll down
                            self.print_history(options, start_index)
                            

                    elif direction == -1:  # Rotary encoder counter-clockwise
                        if self.current_selection > 1:
                            self.current_selection -= 1
                            if self.current_selection < start_index + 1:
                                start_index -= 1  # Scroll up
                            self.print_history(options, start_index)

                    elif direction == 2:  # Rotary encoder button pressed
                        self.selection = self.current_selection  # Match the state with the options
                        #print(self.selection)
                        self.current_selection = 1
                        return self.selection
                time.sleep(0.1)
            else:
                oled.text("No data",10,20,1)
                oled.text("to show",10,30,1)
        
"""
display = DisplayControl()
display.hr_collect()"""