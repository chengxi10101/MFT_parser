from .MFT import MFT

class ATTR(MFT): #common header
    structure = [
        ["ATTR_TYPE", 0, 4],
        ["LENGTH", 4, 4],
        ["NR_FLAG", 8, 1],
        ["NAME_LENGTH", 9, 1],
        ["NAME_OFFSET", 10, 2],
        ["FLAG", 12, 2],
        ["ATTR_ID", 14, 2],
    ]
