from pprint import pprint
import os
import csv
from database import session, MFT, init_db
from datetime import datetime
import pymft.Header
import pymft.ATTR 
import pymft.AttrData
import pymft.Resident
import pymft.NameLenOffset
import argparse

def getMFT(path):
    f = open(path, "rb")
    mft = f.read()
    f.close()
    return [mft[i:i+1024] for i in range(0, len(mft), 1024)]

def parse(filename):

    mft = getMFT(filename)
    cnt = 0
    lst = []
    for m in mft: # test eg. mft[:166]

        cnt += 1
        # 1. MFT entry header parsing
        header = pymft.Header(data=m)
        header.parse()
        if header.parsed['SIGNATURE'][0] != b'FILE': continue

        pprint(header.parsed) #
        # print("%d. MFT"%(cnt))

        # ATTRIBUTE PART
        offset = header.parsed['OFFSET_TO_FIRST_ATTR'][1] #0x38
        data_attrs = []
        while True:
            # FFFFFFFF인 경우 종료
            if m[offset:offset+4] == b"\xff\xff\xff\xff": break

            # 2. Common header parsing
            attr = pymft.ATTR(data=m[offset:]) #0x38~
            attr.parse()
            # 예외처리
            if attr.parsed['LENGTH'][1] == 0: break

            common_header_length = 16 #고정크기
            pivot = offset+common_header_length #다음 섹터 범위 : 0x38 ~ 38+16

            # 3. Resident/Non-Resident structure parsing
            non_resident_flag = attr.parsed['NR_FLAG'][1]
            if non_resident_flag == 1:
                res_length = 48
            else:
                res_length = 8
            resident = pymft.Resident(data=m[pivot:pivot+res_length], code=non_resident_flag) #code : 1=non-resident
            resident.parse()
            pivot = pivot+res_length
            pprint(resident.parsed) #

            # 4. Attribute Name parsing (if exist..)
            name_len = attr.parsed['NAME_LENGTH'][1] #name length 기준 이름 여부 판별
            if name_len == 0:
                noname = 1
            else:
                noname = 0 
                attrname = pymft.NameLenOffset(data=m[pivot:pivot+name_len], code=noname) #code : 1 = noname
                attrname.parse()
                pprint(attrname.parsed) #
                #pivot = pivot + name_len (이름뒤에 dummy 들어가서 이걸로 하면 안됨)

            # 5. Attribute Data parsing (AttrData)
            attr_offset = 0
            attr_length = -1
            if non_resident_flag == 1:
                attr_offset = resident.parsed['DATA_RUN_OFFSET'][1]
            else:
                attr_offset = resident.parsed['ATTR_DATA_OFFSET'][1] #common_header부터 얼만큼의 offset을 뛰었는지
                attr_length = resident.parsed['ATTR_LENGTH'][1]
            pivot = offset + attr_offset
            pprint(resident.parsed) #
            attr_data_raw = m[pivot:] if attr_length == -1 else m[pivot:pivot+attr_length]
            attr_data = pymft.AttrData(
                            data=attr_data_raw,
                            code=attr.parsed['ATTR_TYPE'][1],
                            non_resident_flag=non_resident_flag,
                            attr_header=attr.parsed,
                            resident=resident.parsed
                        )
            attr_data.parse()
            pprint(attr_data.parsed) #

            # Next ATTRIBUTE
            offset += attr.parsed['LENGTH'][1] #attribute_length(common ~ attr_data)

            # 출력
            data = {}
            data.update(attr.parsed)
            data.update(attr_data.parsed)
            data_attrs.append(data)

        data = {}
        data.update(header.parsed)
        data.update(resident.parsed)
        data['attrs'] = data_attrs
        for a in data_attrs: data.update(a)
        data.update(attr_data.parsed)
        lst.append(data)
        #print(cnt, data.get("FILENAME", [b'', 0])[0].decode("utf-16"))
    return lst

def parse_filetime(qword):
    # see http://integriography.wordpress.com/2010/01/16/using-phython-to-parse-and-present-windows-64-bit-timestamps/
    time_delta = 3600 * 9 # 9시간
    return datetime.utcfromtimestamp(float(qword) * 1e-7 - 11644473600 + time_delta)

def main():
    parser = argparse.ArgumentParser(description='Usage: python3 app.py --i "./extracted_MFT" --f "csv||db"')
    parser.add_argument('--i', required=True, help="input file")
    parser.add_argument('--f', required=True, help="select format: csv or db")
    args = parser.parse_args()

    filename = args.i #"./extracted_MFT"
    lst = parse(filename)

    if args.f == 'csv':
        f = open('result.csv','w', newline='')
        wr = csv.writer(f)
        for row in lst:
            # type : CSV 
            wr.writerow([
                row.get("FILENAME", [b'', 0])[0].decode("utf-16"), #2B
                int.from_bytes(row.get("REAL_SIZE", [b'', 0])[0], byteorder = 'little'),

                parse_filetime(row.get("FILE_CREATED1", [b'', 0])[1]),
                parse_filetime(row.get("FILE_MODIFIED1", [b'', 0])[1]),
                parse_filetime(row.get("RECORD_CHANGED1", [b'', 0])[1]),
                parse_filetime(row.get("LAST_ACCESS1", [b'', 0])[1]),
                parse_filetime(row.get("FILE_CREATED", [b'', 0])[1]),
                parse_filetime(row.get("FILE_MODIFIED3", [b'', 0])[1]),
                parse_filetime(row.get("RECORD_CHANGED3", [b'', 0])[1]),
                parse_filetime(row.get("FILE_MODIFIED3", [b'', 0])[1]),
                parse_filetime(row.get("LAST_ACCESS3", [b'', 0])[1]),

                int.from_bytes(row.get("FLAG_IN_USE", [b'', 0])[0], byteorder = 'little'), #1=존재, 0=삭제, 
                #row.get("FILE_FULL_PATH", [b'', 0])[0].decode("utf-16"),
            ])
        f.close()
    elif args.f == 'db':
        init_db()
        for row in lst:
            # type : DB
            session.add(MFT(
                file_name = row.get("FILENAME", [b'', 0])[0].decode("utf-16"),
                file_size = int.from_bytes(row.get("REAL_SIZE", [b'', 0])[0], byteorder = 'little'), #non-resident

                s_created_time = parse_filetime( row.get("FILE_CREATED1", [b'', 0])[1] ),
                s_modified_time = parse_filetime( row.get("FILE_MODIFIED1", [b'', 0])[1] ),
                s_mft_modified_time = parse_filetime( row.get("RECORD_CHANGED1", [b'', 0])[1] ),
                s_last_accessed_time = parse_filetime( row.get("LAST_ACCESS1", [b'', 0])[1] ),
                f_created_time = parse_filetime( row.get("FILE_CREATED3", [b'', 0])[1] ),
                f_modified_time = parse_filetime( row.get("FILE_MODIFIED3", [b'', 0])[1] ),
                f_mft_modified_time = parse_filetime( row.get("RECORD_CHANGED3", [b'', 0])[1] ),
                f_last_accessed_time = parse_filetime( row.get("LAST_ACCESS3", [b'', 0])[1] ),

                is_deleted = int.from_bytes(row.get("FLAG_IN_USE", [b'', 0])[0], byteorder = 'little'),
                #file_full_path = row.get("FILE_FULL_PATH", [b'', 0])[0].decode("utf-16"),
            ))
        session.commit()
    else:
        print("Invalid format :(")

if __name__ == "__main__":
    main()