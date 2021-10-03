import io
import struct
import os
import collections
import sys

sda_glob = []
sda_folder = "."

if len(sys.argv) > 1:
    sda_folder = sys.argv[1]
    print (" [i] using provided folder path `%s`..." % sda_folder)
else:
    print (" [i] using current folder to search and fix DDS files...")


# swy: here's the real meat
def parse_data_slice(needed_magic, file_path):
    with open(file_path, 'rb+') as f:
        magic = struct.unpack('4s', f.read(4))[0]
        print(magic)
        if not magic == needed_magic:
            return None
        #f.seek(0x54)
        #fourc = struct.unpack('4s', f.read(4))[0];

try:
    from pathlib import Path
    sda_glob = Path(sda_folder).glob('data_slice_*.dat')

except: # swy: python 2 does not include pathlib by default, so fallback to this: https://stackoverflow.com/a/2186565/674685
    import fnmatch
    import os
    
    matches = []
    for root, dirnames, filenames in os.walk(sda_folder):
        for filename in fnmatch.filter(filenames, 'data_slice_*.dat'):
            sda_glob.append(os.path.join(root, filename))

data = []

# swy: aggregate the bundled application data, each number is a regional prefix
for file_path in sda_glob:
    print(" [>] opening %s" % file_path)

    cur = parse_data_slice('MTZF', file_path)
    if cur:
        data += cur 

    break

# swy: apply the downloaded update; hopefully the data will be fresher this way
data_update = parse_data_slice('MTZD', "data_slice_downloaded_update.bin")


# swy: dump the result
print("\n".join(data))