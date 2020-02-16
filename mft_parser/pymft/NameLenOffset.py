from .MFT import MFT

class NameLenOffset(MFT):
    def __init__(self, data, code, attr_header={}):
        self.data = data
        self.structure = []
        self.parsed = {}
        # code = noname
        if code == 1:
            self.structure = [
                ["ATTR_NAME", 0, 2*attr_header['NAME_LENGTH'][1]],
            ]