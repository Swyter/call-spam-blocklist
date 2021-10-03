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



data = {}

# swy: here's the real meat
def parse_data_slice(needed_magic, file_path):
    ret_data = {}
    with open(file_path, 'rb+') as f:
        magic = struct.unpack('4s', f.read(4))[0]

        print(" [>] opening %s [%s] " % (file_path, magic), needed_magic)

        if not magic.decode('ascii') == needed_magic:
            return None

        print(" [&] magic value matches")

        f.seek(0xf)
        added_item_count = struct.unpack('<I', f.read(4))[0]; print(added_item_count)

        for i in range(0, added_item_count):
            #print(i)
            tlf      = struct.unpack('<Q', f.read(8))[0];
            positive = struct.unpack('<B', f.read(1))[0];
            negative = struct.unpack('<B', f.read(1))[0];
            neutral  = struct.unpack('<B', f.read(1))[0];
            unk_zero_padding_maybe = struct.unpack('<B', f.read(1))[0];
            category = struct.unpack('<B', f.read(1))[0];

            category_tags = [
                "cat_choose_category",
                "cat_telemarketer",
                "cat_debt_collector",
                "cat_silent_call",
                "cat_nuisance_call",
                "cat_unsolicited_call",
                "cat_call_centre",
                "cat_fax_machine",
                "cat_non_profit_org",
                "cat_political_call",
                "cat_scam_call",
                "cat_prank_call",
                "cat_sms",
                "cat_survey",
                "cat_other",
                "cat_finance_service",
                "cat_company",
                "cat_service",
                "cat_robocall"
            ]
            
            #print(tlf, positive, negative, neutral, category, category_tags[category])
            ret_data[tlf] = (positive, negative, neutral, category, category_tags[category])

        cp = struct.unpack('2s', f.read(2))[0]; print(cp)
        if not cp.decode('ascii') == 'CP':
            return None

        removed_item_count = struct.unpack('<I', f.read(4))[0]
        print(removed_item_count)

        for i in range(0, removed_item_count):
            tlf = struct.unpack('<Q', f.read(8))[0];
            #print(i, tlf)
            ret_data.pop(tlf, None)
        #print("ret_data", ret_data)
        return ret_data
        

# swy: aggregate the bundled application data, each number is a regional prefix
for file_path in sda_glob:
    cur = parse_data_slice('MTZF', file_path); # print(cur)
    if cur:
        data.update(cur) 

    #break

# swy: apply the downloaded update; hopefully the data will be fresher this way
data_update = parse_data_slice('MTZD', "data_slice_downloaded_update.bin")

data.update(data_update)
# swy: dump the result

#print(data)

print("\n".join(["+" + str(elem) for i, elem in enumerate(data)]))