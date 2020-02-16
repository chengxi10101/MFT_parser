from .MFT import MFT

class Resident(MFT):
    def __init__(self, data, code, attr_header={}):
        self.data = data
        self.structure = []
        self.parsed = {}
        # flag = code 
        if code == 0:
            self.structure = [ # resident
                ["ATTR_LENGTH", 0, 4], #
                ["ATTR_DATA_OFFSET", 4, 2], #
                ["INDEXED_FLAG", 6, 1],
                ["PADDING", 7, 1],
            ]
        elif code == 1:
            self.structure = [ # non-resident
                ["FITST_VCN", 0, 8],
                ["LAST_VCN", 8, 8], 
                ["DATA_RUN_OFFSET", 16, 2],  #
                ["COMPRESSION_UNIT_SIZE", 18, 2], 
                ["PADDING", 20, 4], 
                ["ALLOCATED_SIZE", 24, 8],
                ["REAL_SIZE", 32, 8], 
                ["INITIALIZED_SIZE", 40, 8],
            ]

# resident : 
# SIZE_OF_CONTENT(4), OFFSET_TO_CONTENT(2), IDX_FLAG(1), UNUSED(1), 
# ATTRIBUTE_NAME(속성이 있는경우 이름, 없는경우 바로 속성 적용)

# non-resident :
# START_VCN_OF_THE_RUNLIST(8), END_VCN_OF_THE_RUNLIST(8), OFFSET_TO_RUNLIST(2), COMP_UNIT_SIZE(2),
#  UNUSED(4), ALLOCATED_SIZE_OF_ATTRIBUTE_CONTENT(8), REAL_SIZE_OF_ATTRIBUTE_CONTENT(8),
#  INITIALIZED_SIZE_OF_ATTRIBUTE_CONTENT(8), ATTRIBUTE_NAME(?if exist)