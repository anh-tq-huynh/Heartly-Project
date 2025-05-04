from PIL import Image

def image_to_bytearray(image_path):
    img = Image.open(image_path).convert('1')  # Convert to 1-bit monochrome
    width, height = img.size
    pixels = list(img.getdata())
    byte_array = bytearray()

    for y in range(0, height, 8):
        for x in range(width):
            byte = 0
            for bit in range(8):
                if y + bit < height:
                    pixel = pixels[x + (y + bit) * width]
                    if pixel == 0:  # Black pixel
                        byte |= (1 << bit)
            byte_array.append(byte)

    return byte_array, width, height

image_path = "logo.png" #The logo must be black and white.
byte_array, width, height = image_to_bytearray(image_path)

print(byte_array)
print(width)
print(height)