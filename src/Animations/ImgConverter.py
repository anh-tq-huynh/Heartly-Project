from PIL import Image
import json

class ImgConverter:
    def __init__(self,path):
        self.path = path

    def load_img(self):
        img = Image.open(self.path).convert("1")
        bitmap = list(img.getdata())
        return bitmap

    def bitmap_to_array(self,bitmap):
        array = []
        for height in range(0,64,8):
            for width in range(0,128):
                byte = 0
                for bit in range(0,8):
                    #find the index of the current pixel in the list bitmap
                    # which row defined by (height(height group as it increment by 8) + bit (which row in the height group))
                    pixel_index = 128*(height+bit) + width
                    if height + bit < len(bitmap) :
                        if bitmap[pixel_index] == 255:
                            byte |= 1<<bit
                array.append(byte)
        return array

    def format(self,result_array):
        converted_array = list(bytearray(result_array))
        formatted = "["
        for i,value in enumerate(converted_array):
            formatted += str(value)
            if i < len(converted_array) -1:
                formatted += ","
            if i % 50 == 0:
                formatted += "\n"
        formatted += "]"
        return formatted

    def conversion(self):
        load_img = self.load_img()
        bitmap = self.bitmap_to_array(load_img)
        #formatted = self.format(bitmap)
        return bitmap

def list_bytearray(list,img_path):
    img = ImgConverter(img_path)
    list.append(img.conversion())
    return list

list_array = []
paths = [
    "ezgif-split/frame_00_delay.png",
    "ezgif-split/frame_01_delay.png",
    "ezgif-split/frame_02_delay.png",
    "ezgif-split/frame_03_delay.png",
    "ezgif-split/frame_04_delay.png",
    "ezgif-split/frame_05_delay.png",
    "ezgif-split/frame_06_delay.png",
    "ezgif-split/frame_07_delay.png",
    "ezgif-split/frame_08_delay.png",
    "ezgif-split/frame_09_delay.png",
    "ezgif-split/frame_10_delay.png",
    "ezgif-split/frame_11_delay.png",
    "ezgif-split/frame_12_delay.png",
    "ezgif-split/frame_13_delay.png",
    "ezgif-split/frame_14_delay.png",
]

for path in paths:
    list_bytearray(list_array,path)

byte_arrays = []
for item in list_array:
    byte_arrays.append(bytearray(item))

print(byte_arrays[14])