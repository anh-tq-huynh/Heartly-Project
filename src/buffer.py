class RoundRobin:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.is_full = False

    def append(self, item):
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.size

        if self.is_full:
            self.tail = (self.tail + 1) % self.size

        if self.head == self.tail:
            self.is_full = True

    def get(self):
        if not self.is_full and self.head == self.tail:
            return []  # buffer is empty

        items = []
        idx = self.tail

        while True:
            items.append(self.buffer[idx])
            if idx == self.head - 1 and not (self.is_full and self.head == self.tail):
                break
            idx = (idx + 1) % self.size
            if idx == self.tail:
                break

        return items
    
    def clear(self):
        self.head = 0
        self.is_full = False
        
    def __len__(self):
        if self.is_full:
            return self.size
        if self.head >= self.tail:
            return self.head - self.tail
        return self.size + self.head - self.tail