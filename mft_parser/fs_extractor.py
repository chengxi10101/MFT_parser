import pytsk3, sys
import hashlib
import argparse

parser = argparse.ArgumentParser(description='Usage: python3 fs_extractor.py --i [fs file] ')
parser.add_argument('--i', required=True, help="input file")
args = parser.parse_args()

filename = args.i

img = pytsk3.Img_Info(filename)#sys.argv[1]) #'./'+str(sys.argv[1]) 
fs = pytsk3.FS_Info(img)

f = fs.open('/$MFT') #'/Windows/System32/config/SAM' for eventlog
with open('extracted_MFT','wb') as o:
    buf = f.read_random(0,f.info.meta.size)
    o.write(buf)