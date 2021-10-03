#!/usr/bin/env python3
import struct
import os
import sys

sda_glob = []
sda_folder = "."
sda_target_file = "blocklist_b.txt"

if len(sys.argv) > 1:
    sda_folder = sys.argv[1]
    print (" [i] using provided folder path `%s`..." % sda_folder)
else:
    print (" [i] using current folder to search and fix DDS files...")

# swy: grab the list of files with that filename pattern in the selected folder
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

# swy: here's the real meat; this function reads the custom binary files that store and override the telephone numbers
#      and their metadata; mainly the kind of spam and how many reports of each; good, neutral or bad.
def parse_data_slice(needed_magic, file_path, global_data):
    with open(file_path, 'rb+') as f:

        # swy: see shouldianswer-dataslice.bt and open it with 010 Editor to quickly inspect the format and its fields
        #      this is based on that, made it all today with a bit of tweaking and light reading...
        magic = struct.unpack('4s', f.read(4))[0]

        print(" [>] opening %s [%s] " % (file_path, magic), needed_magic)

        if not magic.decode('ascii') == needed_magic:
            return None

        print(" [&] magic value matches")

        # swy: jump straight to the added_item_count offset, it's an absolute displacement in bytes from the beginning
        #      we could verify things a bit more to ensure correctness, but right now checking the header seems enough
        f.seek(0xf); added_item_count = struct.unpack('<I', f.read(4))[0]; print(added_item_count)

        for i in range(0, added_item_count):
            #print(i)
            tlf      = struct.unpack('<Q', f.read(8))[0];
            positive = struct.unpack('<B', f.read(1))[0];
            negative = struct.unpack('<B', f.read(1))[0];
            neutral  = struct.unpack('<B', f.read(1))[0];
            unk_zero_padding_maybe = struct.unpack('<B', f.read(1))[0];
            category = struct.unpack('<B', f.read(1))[0]; category = 50

            # swy: grabbed from the string table, can be treated like some kind of enum;
            #      careful about unimplemented values/indexes that cause overflows.
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

            # swy: keep in mind that the database also includes positive numbers, so we need to do our own filtering to black list only the bad telephone stuff,
            #      include only those with 1 or more reports and not too many positive counter-reports. keep neutral reviews in check, too.
            if negative >= 1 and negative > positive and negative > neutral:
                global_data[tlf] = (positive, negative, neutral, category, category in category_tags and category_tags[category] or category_tags[0]) # swy: instead of "[¿unknown?]") better if we use a generic category to avoid breakage

        cp = struct.unpack('2s', f.read(2))[0]; print(cp)
        if not cp.decode('ascii') == 'CP':
            return None

        removed_item_count = struct.unpack('<I', f.read(4))[0]
        print(removed_item_count)

        for i in range(0, removed_item_count):
            tlf = struct.unpack('<Q', f.read(8))[0]; #print(i, tlf)
            global_data.pop(tlf, None)
        

# --

# swy: aggregate the bundled application data, each number is a regional prefix
for file_path in sda_glob:
    parse_data_slice('MTZF', file_path, data); # print(cur)
    #break

# swy: apply the downloaded update; hopefully the data will be fresher this way
parse_data_slice('MTZD', "data_slice_downloaded_update.bin", data)

# swy: dump the result
with open(sda_target_file, 'w+') as f:
    f.write("\n".join(["+" + str(elem) for i, elem in enumerate(data)]))