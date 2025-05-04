from filefifo import Filefifo
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
from calculations import HRVAnalysis

# Initialize I2C and OLED
i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Constants
display_width = 128
display_height = 64

def clamp(val, min_val=0, max_val=63):
    global samples_val
    return max(min(samples_val, max_val), min_val)

def scale_sample(value, min_val, max_val):
    if max_val - min_val == 0:
        return 0
    scaled = int((value - min_val) * (display_height - 1) / (max_val - min_val))
    return clamp(display_height - 1 - scaled)

# Get samples and peaks from HRV analysis
hrv = HRVAnalysis(samples)  # Assuming samples are passed to HRVAnalysis
samples_val = samples = hrv.reading()
peaks = hrv.find_peaks()

# Display parameters
window_start = 0
min_val = min(peaks)
max_val = max(peaks)

# Display loop
while window_start <= len(peaks) - display_width:
    oled.fill(0)
    window = peaks[window_start:window_start + display_width]
    for x, sample in enumerate(window):
        y = scale_sample(sample, min_val, max_val)
        oled.pixel(x, y, 1)
    oled.show()
    window_start += 1 
    time.sleep(0)