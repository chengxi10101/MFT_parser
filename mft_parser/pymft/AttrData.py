from .MFT import MFT

def b2i(value):
    return int.from_bytes(value, byteorder='little')

class AttrData(MFT):
    def __init__(self, data, code, non_resident_flag, attr_header={}, resident={}):
        self.data = data
        self.structure = []
        self.parsed = {}
        if code == 0x10: #STD_INFO
            self.structure = [
                ["FILE_CREATED1", 0, 8],
                ["FILE_MODIFIED1", 8, 8],
                ["RECORD_CHANGED1", 16, 8],
                ["LAST_ACCESS1", 24, 8],
                ["PERMISSION", 32, 4],
                ["MAXIMUM_NUMBER_OF_VERSION", 36, 4],
                ["VERSION_NUMBER", 40, 4],
                ["CLASS_ID", 44, 4],
                ["OWNER_ID", 48, 4],
                ["SECURITY_ID", 52, 4],
                ["QUOTA_CHARGED", 56, 8],
                ["UPDATE_SEQUENCE_NUMBER", 64, 8],
            ]
        elif code == 0x20: #ATTRIBUTE_LIST
            if non_resident_flag == 0:
                # 0부터 attribute_Data 영역 모두를 00이 아닐때까지 파싱
                records = []
                off = 0
                while True :
                    #print(records)
                    if 0 < len(records) and records[-1]['TYPE'][1] == 0: break # \x00 인 경우 종료? 더이상 읽을 바이트 X일때까지.
                    record = {
                        "TYPE": data[off:off+4],
                        "RECORD_LENGTH": data[off+4:off+6],
                        "NAME_LENGTH": data[off+6:off+7],
                        "NAME_OFFSET": data[off+7:off+8],
                        "STARTING_VCN": data[off+8:off+16],
                        "BASE_FILE_RECORD_NUMBER": data[off+16:off+22],
                        "BASE_SEQUENCE_NUMBER": data[off+22:off+24],
                        "ATTRIBUTE_ID": data[off+24:off+26],
                        "NAME": data[b2i(data[off+7:off+8]):b2i(data[off+7:off+8])+b2i(data[off+6:off+7])]
                    }
                    for k, v in record.items():
                        record[k] = [v, b2i(v)]
                    records.append(record)
                    off += record['RECORD_LENGTH'][1] #?
                self.parsed['ATTRIBUTE_LIST_RECORD'] = records
            elif non_resident_flag == 1:
                self.structure = [
                    ["ATTRIBUTE_LIST_DATA", 0, resident['ATTR_LENGTH'][1]],
                ]
        elif code == 0x30: #FILE_NAME
            self.structure = [
                ["PARENT_DIRECTORY_FILE_RECORD_NUMBER", 0, 6],
                ["PARENT_DIRECTORY_SEQUENCE_NUMBER", 6, 2],
                ["FILE_CREATED3", 8, 8],
                ["FILE_MODIFIED3", 16, 8],
                ["RECORD_CHANGED3", 24, 8],
                ["LAST_ACCESS3", 32, 8],
                ["ALLOCATE_SIZE", 40, 8], #
                ["FILE_REAL_SIZE", 48, 8],
                ["FILE_ATTRIBUTES", 56, 4],
                ["USED_BY_EAs_AND_REPARSE", 60, 4],
                ["FILENAME_LENGTH", 64, 1],
                ["FILENAME_NAMESPACE", 65, 1],
                ["FILENAME", 66, "FILENAME_LENGTH", 2 ],
            ]
        elif code == 0x40: #OBJECT_ID
            self.structure = [
                ["GUID_OBJECT_ID", 0, resident['ATTR_LENGTH'][1]], #resident.parse()
            ]
        elif code == 0x50: #SECURITY_DESCRIPTOR -> HEADER
            self.structure = [
                ["REVISION", 0, 1],
                ["CONTROL_FLAG", 2, 2], 
                ["OFFSET_TO_USER_SID", 4, 4],
                ["OFFSET_TO_GROUP_SID", 8, 4], 
                ["OFFSET_TO_SACL", 12, 4],
                ["OFFSET_TO_DACL", 16, 4], # 그외 구조체는 disk editor 에 나와 있지 않음
            ]
        elif code == 0x60: #VOLUME_NAME
            self.structure = [
                ["VOLUME_NAME", 0, resident['ATTR_LENGTH'][1] ], # Name length = ATTR_LENGTH로 추정
            ]
        elif code == 0x70: #VOLUME_INFOMATION
            self.structure = [
                ["MAJOR_VERSION", 8, 1],
                ["MINOR_VERSION", 9, 1], 
                ["FALG", 10, 2],
                # 그외 구조체는 disk editor 에 나와 있지 않음
            ]
        elif code == 0x80: #DATA
            if non_resident_flag == 1:
                # DATA가 여러개 오는 non-resident 인 경우 -> 0부터 attribute_Data 영역 모두를 00이 아닐때까지 파싱
                #한바이트 읽어서, nibble 처리 -> 이를 반복...
                data_runs = []
                off = 0
                while True :
                    size = data[off]
                    high = size >> 4
                    low = size & 0xF
                    if high == 0 and low == 0: break # \x00 인 경우 종료
                    off += 1
                    data_runs.append({
                        "CLUSTER_COUNT": data[off:off+low],
                        "FIRST_CLUSTER": data[off+low:off+low+high]
                    })
                    off += low+high
                self.parsed['DATA_RUN'] = data_runs
            elif non_resident_flag == 0:
                self.structure = [ # DATA -> resident
                    ["DATA_DATA", 0, resident['ATTR_LENGTH'][1]],
                ]
        elif code == 0x90: #INDEX_ROOT
            self.structure = [
                #INDEX_ROOT
                ["ATTRIBUTE_TYPE", 0, 4],
                ["COLLATION_RULE", 4, 4], 
                ["SIZE_OF_INDEX_ALLOCATION_ENTRY", 8, 4],
                ["CLUSTERS_PER_INDEX_RECORD", 12, 1],
                #INDEX_HEADER
                ["OFFSET_TO_FIRST_INDEX_ENTRY", 16, 4],
                ["TOTAL_SIZE_OF_THE_INDEX_ENTRIES", 20, 4],
                ["ALLOCATED_SIZE_OF_THE_INDEX_ENTRIES", 24, 4],
                ["FLAGS", 28, 1], 
                # 그 외 구조체는 disk editor 에 X
            ]
        elif code == 0xA0: #INDEX_ALLOCATION
            if non_resident_flag == 1:
                # DATA가 여러개 오는 non-resident 인 경우 -> 0부터 attribute_Data 영역 모두를 00이 아닐때까지 파싱
                # 한바이트 읽어서, nibble 처리 -> 이를 반복...
                data_runs = []
                off = 0
                while True :
                    size = data[off]
                    high = size >> 4
                    low = size & 0xF
                    if high == 0 and low == 0: break # \x00 인 경우 종료
                    off += 1
                    data_runs.append({
                        "CLUSTER_COUNT": data[off:off+low],
                        "FIRST_CLUSTER": data[off+low:off+low+high]
                    })
                    off += low+high
                self.parsed['DATA_RUN'] = data_runs
            elif non_resident_flag == 0:
                self.structure = [ # DATA -> resident
                    ["DATA_DATA", 0, resident['ATTR_LENGTH'][1]],
                ]
        elif code == 0xB0: #BITMAP
            if non_resident_flag == 1:
                # DATA가 여러개 오는 non-resident 인 경우 -> 0부터 attribute_Data 영역 모두를 00이 아닐때까지 파싱
                data_runs = []
                off = 0
                while True :
                    size = data[off]
                    high = size >> 4
                    low = size & 0xF
                    if high == 0 and low == 0: break # \x00 인 경우 종료
                    off += 1
                    data_runs.append({
                        "CLUSTER_COUNT": data[off:off+low],
                        "FIRST_CLUSTER": data[off+low:off+low+high]
                    })
                    off += low+high
                self.parsed['DATA_RUN'] = data_runs
            elif non_resident_flag == 0:
                self.structure = [ # DATA -> resident
                    ["BITMAP_DATA", 0, resident['ATTR_LENGTH'][1]], ### 속성 이름 수정
                ]
        elif code == 0x100: #LOGGED_UTILITY_STREAM
            self.structure = [
                ["LOGGED_UTILITY_STREAM_DATA", resident['ATTR_DATA_OFFSET'][1], resident['ATTR_LENGTH'][1]],
            ]
        elif code == 0x0: # exception 
            pass
        else: 
            print("Invalid Attribute type. > ", hex(code))