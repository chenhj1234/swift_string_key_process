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
show_underscore_to_camel = False
show_underscore_position = False
show_i18n_enum = False
show_fail_qmiix_str_key = False
show_qmiix_const_to_i18n = False

def convert_underscore_to_camel(underscore_str = ""):
    position = 0
    orgstr = underscore_str
    while position >= 0:
        underscore_pos = underscore_str.find('_', position)
        if(underscore_pos >= 0):
            underscore_key = underscore_str[underscore_pos+1:underscore_pos+2]
            if show_underscore_position:
                print(underscore_key)
            underscore_str = underscore_str.replace("_" + underscore_key, underscore_key.upper())
        position = underscore_pos
    
    if show_underscore_to_camel:    
        print(f'Convert {orgstr} to i18n.{underscore_str}')
    return underscore_str

I18N_VAR_DECLA = "internal static let "

def find_char_pos_with_space(str_to_find : str, char_to_mark : str,  offset : int):
    pos1 = str_to_find.find(" ", offset)
    pos2 = str_to_find.find(char_to_mark, offset)
    if (pos1 < 0):
        return pos2
    if (pos2 < 0):
        return pos1
    if pos2 < pos1:
        return pos2
    else:
        return pos1

def get_var_name_and_value(line = "", decla_str = ""):
    if line.find(decla_str) >= 0:
        equality_parts = line.split("=")
        enum_parts = equality_parts[0].split(" ")
        str_id_parts = equality_parts[1].split("\"")
        for enum_name in reversed(enum_parts):
            if(enum_name.find(" ") < 0 and len(enum_name) > 0):
                break
        for str_id_name in reversed(str_id_parts):
            if re.match(r'^\w+', str_id_name, re.M|re.I):
                break
        return enum_name, str_id_name


# Read i18n file and generate string key to enum dictionary
def convert_underscore_to_camel_from_i18n(i18n_file):
    i18ndict = {}
    with open(i18n_file, "r") as i18nfile:
        lines = i18nfile.readlines()
        for oneline in lines:
            if oneline.find(I18N_VAR_DECLA) >= 0:
                enum_name, str_id_name = get_var_name_and_value(oneline, I18N_VAR_DECLA)
                #equality_parts = oneline.split("=")
                #enum_parts = equality_parts[0].split(" ")
                #str_id_parts = equality_parts[1].split("\"")
                #for enum_name in reversed(enum_parts):
                #    if(enum_name.find(" ") < 0 and len(enum_name) > 0):
                #        break
                #for str_id_name in reversed(str_id_parts):
                #    if re.match(r'^\w+', str_id_name, re.M|re.I):
                #        break
                i18ndict[str_id_name] = enum_name
    return i18ndict


def get_string_id_dictionary(fname, i18ndict = {}):
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
            if row["iOS_ID"] or row["iOS_ID1"] or row["String_en_US"]:
                #print(f'#### new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
                if row["iOS_ID"]:
                    id_dict[row["iOS_ID"]] = row["String_Key"]
                    id_dict[row["iOS_ID"] + "_UNDERSCORE_VAR_TO_CAMEL"] = i18ndict[row["String_Key"]]
                    if show_i18n_enum:
                        print(f'Strin {row["iOS_ID"]} convert to {row["String_Key"]} and i18n enum {i18ndict[row["String_Key"]]}')
                if row["iOS_ID1"]:
                    id_dict[row["iOS_ID1"]] = row["String_Key"]
                    id_dict[row["iOS_ID1"] + "_UNDERSCORE_VAR_TO_CAMEL"] = i18ndict[row["String_Key"]]
                    if show_i18n_enum:
                        print(f'Strin {row["iOS_ID1"]} convert to {row["String_Key"]} and i18n enum {i18ndict[row["String_Key"]]}')
                if row["String_en_US"]:
                    id_dict[row["String_en_US"]] = row["String_Key"]
                    id_dict[row["String_en_US"] + "_UNDERSCORE_VAR_TO_CAMEL"] = i18ndict[row["String_Key"]]
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
    funckeys = []
    begin = 0
    position = 0
    while begin >= 0:
        position = nsstring.find("NSLocalizedString" ,begin)
        if position >= 0:
            if nsstring.find("self,", position) < 0:
                key_comma = nsstring.find(",", position + 5)
                key_position = nsstring.find("\"", position + 5)
                key_end = nsstring.find("\"", key_position + 1)
                full_key_end = nsstring.find(")", key_position + 1)
                if key_position >= 0:
                    # and key_comma > key_position:
                    # and key_position + 1 < key_end:
                    keys.append(nsstring[key_position + 1:key_end])
                    funckeys.append(nsstring[position:full_key_end + 1])
            begin = position + 5
        else:
            begin = position
    return keys, funckeys

def find_ns_string_key_list_full_function(nsstring):
    keys = []
    begin = 0
    position = 0
    while begin >= 0:
        position = nsstring.find("NSLocalizedString" ,begin)
        if position >= 0:
            if nsstring.find("self,", position) < 0:
                key_comma = nsstring.find(",", position + 5)
                key_position = nsstring.find("\"", position + 5)
                key_end = nsstring.find(")", key_position + 1)
                if key_position >= 0:
                    # and key_comma > key_position:
                    # and key_position + 1 < key_end:
                    keys.append(nsstring[position:key_end + 1])
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
        stringkeys, fullkeys = find_ns_string_key_list(oneline)
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

def get_nsstring_key_from_code_and_replace(fname, key_dict, replace_fname, fail_log_file = open("log.txt", "w")):
    sourcefile = open(fname, mode='r')
    targetfile = open(replace_fname, mode='w')
    #fail_log_file = open(logfile, mode='a')
    lines = sourcefile.readlines()
    for index, oneline in enumerate(lines):
        stringkeys, stringkeys_func = find_ns_string_key_list(oneline)
        # stringkeys_func = find_ns_string_key_list_full_function(oneline)
        for keyind, stringkey in enumerate(stringkeys):
            if show_detail_message:
                print(f'Find key:{stringkey} in line {oneline}')
            elif show_find_nsstring_key:
                print(f'Find key:{stringkey}')
            try:
                replace_key = stringkeys_func[keyind]
                new_key = "i18n." + key_dict[stringkey + "_UNDERSCORE_VAR_TO_CAMEL"]
                if show_success_key:
                    print (f'{stringkey} to {new_key}')
                oneline = oneline.replace(replace_key, new_key)
            except KeyError:
                if show_fail_key:
                    if show_fail_key_with_file:
                        print (f'{stringkey} not exist in file {fname} line {index}')
                        print (f'{stringkey} not exist in file {fname} line {index}', file = fail_log_file)
                    else:
                        print (f'{stringkey} not exist')
                        print (f'{stringkey} not exist', file = fail_log_file)

        lines[index] = oneline
    targetfile.writelines(lines)
    sourcefile.close()
    targetfile.close()
    #fail_log_file.close()

def fix_swift_file_in_filepath(src_dname, dst_dname, key_dict):
        fnames = get_swift_file(src_dname)
        fail_log_file = open("log.txt", mode='w')
        for targetfile in fnames:
            replacefile = targetfile.replace(src_dname, dst_dname)
            if show_processing_files:
                print(f'Processing file {onefile} ...')
            get_nsstring_key_from_code_and_replace(targetfile, idd, replacefile, fail_log_file = fail_log_file)
        fail_log_file.close()

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

QMIIX_STR_DECLA = "static let"

def fix_QMIIX_String_class(const_file = "QMConstants.swift", key_dict = {}, fail_log_file = open("miix_str_error.log", "w")):
    class_find_status = "not found"
    with open(const_file, "r") as miix_const:
        constlines = miix_const.readlines()
        miix_const.close()
        for index, constline in enumerate(constlines):
            if constline.find("QMIIX_String") >= 0:
                class_find_status = "found"
            elif class_find_status == "found" and constline.find("}") >= 0:
                class_find_status = "finished"
            if class_find_status == "found" and constline.find(QMIIX_STR_DECLA) >= 0:
                varname, varvalue = get_var_name_and_value(constline, QMIIX_STR_DECLA)
                try:
                    i18nstr = key_dict[varvalue]
                    i18ndecstr = key_dict[varvalue + "_UNDERSCORE_VAR_TO_CAMEL"]
                    constlines[index] = constline.replace("\"" + varvalue + "\"" , "i18n." + i18ndecstr)
                    if show_qmiix_const_to_i18n:
                        print(f'Find {varvalue} for {i18nstr} and {i18ndecstr}')
                except KeyError:
                    if show_fail_qmiix_str_key:
                        print(f'{varvalue} not found in line {index} content {constline}')
                    print(f'{varvalue} not found in line {index}', file = fail_log_file)
        with open(const_file, "w") as const_write:
            const_write.writelines(constlines)
            const_write.close()
    fail_log_file.close()

if __name__ == "__main__" :
    #print('Number of arguments: {}'.format(len(sys.argv)))
    if (len(sys.argv) < 2):
        print('Usage process_csv_string.py csvfile')
        exit(1)
    #print('Argument(s) passed: {}'.format(str(sys.argv)))


    #/Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift
    if len(sys.argv) > 3:
        src_dname = sys.argv[2]
        dst_dname = sys.argv[3]
        i18ndict = convert_underscore_to_camel_from_i18n(src_dname + "/SwiftGenFiles/outputs/i18n.swift")
        idd = get_string_id_dictionary(sys.argv[1], i18ndict)
        fix_swift_file_in_filepath(src_dname, dst_dname, idd)
        fix_QMIIX_String_class("/Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift", idd)
    elif len(sys.argv) > 2:
        targetfile = sys.argv[2]
        i18ndict = convert_underscore_to_camel_from_i18n("i18n.swift")
        idd = get_string_id_dictionary(sys.argv[1], i18ndict)
        replacefile = "new_" + targetfile
        get_nsstring_key_from_code_and_replace(targetfile, idd, replacefile)
        #get_nsstring_key_list_from_code(targetfile, idd)
    else:
        fnames = get_swift_file("/Users/admin/projects/qmiix/qmiix-ios")
        for onefile in fnames:
            if show_processing_files:
                print(f'Processing file {onefile} ...')
            get_nsstring_key_from_code(onefile, idd)
