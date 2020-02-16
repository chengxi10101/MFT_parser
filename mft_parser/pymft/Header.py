from .MFT import MFT

class Header(MFT):
    structure = [
        ["SIGNATURE", 0, 4],
        ["OFFSET_TO_FIXUP_ARRAY", 4, 2],
        ["NUMBER_OF_ENTRIES_IN_FIXUP_ARRAY", 6, 2],
        ["LOGFILE_SEQUENCE_NUMBER", 8, 8],
        ["SEQUENCE_VALUE", 16, 2], 
        ["HARD_LINK_COUNT", 18, 2],
        ["OFFSET_TO_FIRST_ATTR", 20, 2],
        ["FLAG_IN_USE", 22, 2], # in use flag
        ["USED_SIZE_OF_MFT_ENTRY", 24, 4],
        ["ALLOCATED_SIZE_OF_MFT_ENTRY", 28, 4],
        ["FILE_REFERENCE_BASED_RECODE", 32, 8],
        ["NEXT_ATTR_ID", 40, 2],
        ["DUMMY_0", 42, 2],
        ["ID_OF_THIS_RECORD", 44, 4],
        ["UPDATE_SEQUENCE_NUMBER", 48, 2],
        ["UPDATE_SEQUENCE_ARRAY", 50, 4],
        ["DUMMY_1", 54, 2],
    ]
