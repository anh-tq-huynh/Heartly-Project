from array import array

class RoundRobin:
    def __init__(self, size, typecode='H'):
        """
        Initialize a fixed-size round-robin buffer using array for unsigned integers.
        :param size: maximum number of elements
        :param typecode: typecode for array (defaults to unsigned 16-bit 'H')
        """
        self.size = size
        self.typecode = typecode
        self.buffer = array(self.typecode, [0] * size)
        self.head = 0
        self.tail = 0
        self.is_full = False

    def append(self, item):
        """Append an unsigned integer to the buffer, overwriting oldest when full."""
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.size

        if self.is_full:
            self.tail = (self.tail + 1) % self.size

        if self.head == self.tail:
            self.is_full = True

    def get(self):
        """
        Retrieve buffer contents in insertion order as an array of unsigned ints.
        """
        if not self.is_full and self.head == self.tail:
            # buffer is empty
            return array(self.typecode, [])

        length = len(self)
        result = array(self.typecode, [0] * length)
        idx = self.tail
        for i in range(length):
            result[i] = self.buffer[idx]
            idx = (idx + 1) % self.size
        return result

    def clear(self):
        """Reset the buffer to empty."""
        self.head = 0
        self.tail = 0
        self.is_full = False

    def __len__(self):
        """Return number of elements currently in buffer."""
        if self.is_full:
            return self.size
        if self.head >= self.tail:
            return self.head - self.tail
        return self.size + self.head - self.tail