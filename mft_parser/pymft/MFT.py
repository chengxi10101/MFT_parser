class MFT:
    structure = [
    ]

    def __init__(self, data):
        self.data = data
        self.parsed = {}

    def parse(self):
        for field in self.structure:
            offset = field[1] #int
            length = field[2] if type(field[2]) == int else self.parsed[field[2]][1] * field[3]
            value = self.data[offset:offset+length]
            self.parsed[field[0]] = [ #byte
                value,
                int.from_bytes(value, byteorder='little')
            ]
