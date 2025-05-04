##Animation of the waiting screen
from src.hardware import Display
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import framebuf,time

def waiting_screen(text_input, oled):
        A = bytearray([
            0x00, 0x00, 0xFC, 0x04, 0x02, 0xD2, 0x09, 0x09,
            0x09, 0xD1, 0x02, 0x06, 0xFC, 0x00, 0x00, 0x00,
            0x3C, 0x26, 0x62, 0x43, 0x76, 0x1C, 0x04, 0x04,
            0x04, 0x04, 0x1E, 0x73, 0x42, 0x62, 0x26, 0x3C
        ])
        B = bytearray([
            0x7C, 0x8C, 0x6C, 0x4C, 0x7C, 0x78, 0x40, 0x40,
            0x40, 0x40, 0x78, 0x7C, 0x4C, 0x6C, 0x8C, 0x7C,
            0x1F, 0x60, 0x80, 0x91, 0x8A, 0x84, 0x80, 0xA0,
            0x80, 0x80, 0x8C, 0x82, 0x8C, 0x80, 0x60, 0x13
        ])

        image = framebuf.FrameBuffer(A, 16, 16, framebuf.MONO_VLSB)
        image2 = framebuf.FrameBuffer(B, 16, 16, framebuf.MONO_VLSB)

        text = text_input
        dot = "."
        dot_start = 12 * 8
        y = int(64 / 2)

        oled.text(text, 0, y, 1)
        oled.show()

        for i in range(3):
            oled.fill_rect(0, 0, 16, 16, 0)
            oled.fill_rect(112, 48, 16, 16, 0)
            oled.text(dot, dot_start + i * 8, y, 1)
            oled.blit(image, 0, -25 + (i*10))
            oled.blit(image2, 112, 68 - (i*10))
            oled.show()
            time.sleep(0.5)

        oled.fill_rect(0, 0, 16, 16, 0)
        oled.fill_rect(112, 48, 16, 16, 0)
        oled.text(dot, dot_start, y, 0)
        oled.text(dot, dot_start + 8, y, 0)
        oled.text(dot, dot_start + 16, y, 0)
        oled.show()
        time.sleep(1)