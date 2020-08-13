import csv
import sys
import re
import os

show_detail_message = False
show_success_key = False
show_find_nsstring_key = False
show_fail_key = True
show_fail_key_with_file = True
show_swift_files = False
show_processing_files = False

def get_string_id_dictionary(fname):
    id_dict = {}
    with open(fname, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                # print(f'Column names are {line_count}')
                line_count += 1
            # print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
            if row["iOS_ID"] or row["iOS_ID1"]:
                #print(f'#### new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
                if row["iOS_ID"]:
                    id_dict[row["iOS_ID"]] = row["String_Key"]
                if row["iOS_ID1"]:
                    id_dict[row["iOS_ID1"]] = row["String_Key"]
            elif row["String_en_US"]:
                id_dict[row["String_en_US"]] = row["String_Key"]
            elif not row["String_Key"]:
                print(f'**** new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
            else:
                #print(f'%%%% new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
                #id_dict[row["String_Key"]] = row["iOS_ID"];
                print(f'%%%% new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
            line_count += 1
        #print(f'Processed {line_count} lines.')
        return id_dict

def find_ns_string_key_list(nsstring):
    keys = []
    begin = 0
    position = 0
    while begin >= 0:
        position = nsstring.find("NSLocalizedString" ,begin)
        if position >= 0:
            key_comma = nsstring.find(",", position + 5)
            key_position = nsstring.find("\"", position + 5)
            key_end = nsstring.find("\"", key_position + 1)
            if key_position >= 0:
                # and key_comma > key_position:
                # and key_position + 1 < key_end:
                keys.append(nsstring[key_position + 1:key_end])
            begin = position + 5
        else:
            begin = position
    return keys

def find_ns_string_key(nsstring):
    matchObj = re.match( r'.*NSLocalizedString *\( *\"(\w*)\" *, *.*', nsstring, re.M|re.I)
    if matchObj:
        return matchObj.group(1)
    else:
        return None


def get_nsstring_key_list_from_code(fname, key_dict):
    sourcefile = open(fname, mode='r')
    lines = sourcefile.readlines()
    for oneline in lines:
        stringkeys = find_ns_string_key_list(oneline)
        for stringkey in stringkeys: 
            if show_detail_message:
                print(f'Find key:{stringkey} in line {oneline}')
            elif show_find_nsstring_key:
                print(f'Find key:{stringkey}')
            try:
                new_key = key_dict[stringkey]
                if show_success_key:
                    print (f'{show_success_key} {key_dict[stringkey]}')
            except KeyError:
                if show_fail_key:
                    if show_fail_key_with_file:
                        print (f'{stringkey} not exist in file {fname}')
                    else:
                        print (f'{stringkey} not exist')

def get_nsstring_key_from_code(fname, key_dict):
    sourcefile = open(fname, mode='r')
    lines = sourcefile.readlines()
    for oneline in lines:
        stringkey = find_ns_string_key(oneline)
        if stringkey:
            if show_detail_message:
                print(f'Find key:{stringkey} in line {oneline}')
            elif show_find_nsstring_key:
                print(f'Find key:{stringkey}')
            try:
                new_key = key_dict[stringkey]
                if show_success_key:
                    print (f'{show_success_key} {key_dict[stringkey]}')
            except KeyError:
                if show_fail_key:
                    if show_fail_key_with_file:
                        print (f'{stringkey} not exist in file {fname}')
                    else:
                        print (f'{stringkey} not exist')
            #if key_dict[stringkey]:
            #    print(f'Find new string id {key_dict[stringkey]}')
            #else:
            #    print(f'#### Not string id for string {stringkey}');

def get_nsstring_key_from_code_and_replace(fname, key_dict, replace_fname, logfile = "log.txt"):
    sourcefile = open(fname, mode='r')
    targetfile = open(replace_fname, mode='w')
    fail_log_file = open(logfile, mode='a')
    lines = sourcefile.readlines()
    for index, oneline in enumerate(lines):
        stringkeys = find_ns_string_key_list(oneline)
        for stringkey in stringkeys: 
            if show_detail_message:
                print(f'Find key:{stringkey} in line {oneline}')
            elif show_find_nsstring_key:
                print(f'Find key:{stringkey}')
            try:
                new_key = key_dict[stringkey]
                if show_success_key:
                    print (f'{show_success_key} {key_dict[stringkey]}')
                oneline = oneline.replace(stringkey, new_key)
            except KeyError:
                if show_fail_key:
                    if show_fail_key_with_file:
                        print (f'{stringkey} not exist in file {fname}')
                        print (f'{stringkey} not exist in file {fname}', file = fail_log_file)
                    else:
                        print (f'{stringkey} not exist')
                        fail_log_file.write(f'{stringkey} not exist\n')

        lines[index] = oneline
    targetfile.writelines(lines)
    sourcefile.close()
    targetfile.close()
    fail_log_file.close()

def fix_swift_file_in_filepath(src_dname, dst_dname, key_dict):
        fnames = get_swift_file(src_dname)
        for targetfile in fnames:
            replacefile = targetfile.replace(src_dname, dst_dname)
            if show_processing_files:
                print(f'Processing file {onefile} ...')
            get_nsstring_key_from_code_and_replace(targetfile, idd, replacefile)

def get_swift_file(dname):
    fnames = []
    for root, dirs, files in os.walk(dname):
        for file in files:
            if file.endswith(".swift"):
                fpath = os.path.join(root, file)
                if show_swift_files:
                    print(fpath)
                fnames.append(fpath)
    return fnames

if __name__ == "__main__" :
    #print('Number of arguments: {}'.format(len(sys.argv)))
    if (len(sys.argv) < 2):
        print('Usage process_csv_string.py csvfile')
        exit(1)
    #print('Argument(s) passed: {}'.format(str(sys.argv)))


    idd = get_string_id_dictionary(sys.argv[1])
    if len(sys.argv) > 3:
        src_dname = sys.argv[2]
        dst_dname = sys.argv[3]
        fix_swift_file_in_filepath(src_dname, dst_dname, idd)
    elif len(sys.argv) > 2:
        targetfile = sys.argv[2]
        replacefile = "new_" + targetfile
        get_nsstring_key_from_code_and_replace(targetfile, idd, replacefile)
        #get_nsstring_key_list_from_code(targetfile, idd)
    else:
        fnames = get_swift_file("/Users/admin/projects/qmiix/qmiix-ios")
        for onefile in fnames:
            if show_processing_files:
                print(f'Processing file {onefile} ...')
            get_nsstring_key_from_code(onefile, idd)
