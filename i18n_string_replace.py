import csv
import sys
import re
import os
import fileinput

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

I18N_VAR_DECLA = "internal static let "


def get_var_name_and_value(line="", decla_str=""):
    if line.find(decla_str) >= 0:
        equality_parts = line.split("=")
        enum_parts = equality_parts[0].split(" ")
        str_id_parts = equality_parts[1].split(" ")
        for enum_name in reversed(enum_parts):
            if(enum_name.find(" ") < 0 and len(enum_name) > 0):
                break
        for str_id_name in reversed(str_id_parts):
            if re.match(r'^\w+', str_id_name, re.M | re.I):
                break
        return enum_name, str_id_name.replace("\r","").replace("\n","")


# Read i18n file and generate string key to enum dictionary
def convert_underscore_to_camel_from_i18n(i18n_file):
    i18ndict = {}
    with open(i18n_file, "r") as i18nfile:
        lines = i18nfile.readlines()
        for oneline in lines:
            if oneline.find(I18N_VAR_DECLA) >= 0:
                enum_name, str_id_name = get_var_name_and_value(
                    oneline, I18N_VAR_DECLA)
                # equality_parts = oneline.split("=")
                # enum_parts = equality_parts[0].split(" ")
                # str_id_parts = equality_parts[1].split("\"")
                # for enum_name in reversed(enum_parts):
                #    if(enum_name.find(" ") < 0 and len(enum_name) > 0):
                #        break
                # for str_id_name in reversed(str_id_parts):
                #    if re.match(r'^\w+', str_id_name, re.M|re.I):
                #        break
                i18ndict[str_id_name] = enum_name
    return i18ndict


IOS_KEY_STR = "_IOS_KEY_20200814"
GENERAL_KEY_STR = "_GENERAL_STRING_KEY_20200814"
I18N_KEY_STR = "_UNDERSCORE_VAR_TO_CAMEL"
FIX_REPLACE_ANSWER_POSTFIX = "_REPLACE_ANSWER"


def get_string_id_dictionary(fname, i18ndict={}):
    id_dict = {}
    with open(fname, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                # print(f'Column names are {line_count}')
                line_count += 1
            # print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
            if row["iOS_ID"] or row["iOS_ID1"] or row["String_en_US"]:
                # print(f'#### new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
                if row["iOS_ID"]:
                    id_dict[row["iOS_ID"]] = row["String_Key"]
                    id_dict[row["iOS_ID"] +
                        I18N_KEY_STR] = i18ndict[row["String_Key"]]
                    # Key for distincting ios key and geenral string key
                    id_dict[row["iOS_ID"] +
                        IOS_KEY_STR] = i18ndict[row["String_Key"]]
                    if show_i18n_enum:
                        print(
                            f'Strin {row["iOS_ID"]} convert to {row["String_Key"]} and i18n enum {i18ndict[row["String_Key"]]}')
                if row["iOS_ID1"]:
                    id_dict[row["iOS_ID1"]] = row["String_Key"]
                    id_dict[row["iOS_ID1"] +
                        I18N_KEY_STR] = i18ndict[row["String_Key"]]
                    # Key for distincting ios key and geenral string key
                    id_dict[row["iOS_ID1"] +
                        IOS_KEY_STR] = i18ndict[row["String_Key"]]
                    if show_i18n_enum:
                        print(
                            f'Strin {row["iOS_ID1"]} convert to {row["String_Key"]} and i18n enum {i18ndict[row["String_Key"]]}')
                if row["String_en_US"]:
                    id_dict[row["String_en_US"]] = row["String_Key"]
                    id_dict[row["String_en_US"] +
                        I18N_KEY_STR] = i18ndict[row["String_Key"]]
                    # Key for distincting ios key and geenral string key
                    id_dict[row["String_en_US"] +
                        GENERAL_KEY_STR] = i18ndict[row["String_Key"]]
            elif not row["String_Key"]:
                print(
                    f'**** new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
            else:
                # print(f'%%%% new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
                # id_dict[row["String_Key"]] = row["iOS_ID"];
                print(
                    f'%%%% new id:{row["String_Key"]} old id:{row["iOS_ID"]} value:{row["String_en_US"]}.')
            line_count += 1
        # print(f'Processed {line_count} lines.')
        return id_dict


QMIIX_STR_PREFIX = "QMIIX_String"
show_found_ios_key = False
show_replace_string = True


def search_keys_in_line(linestr: str, qmstr_key_dict: dict):
    new_line_str = ""
    for qmstr_key in qmstr_key_dict:
        if linestr.find(QMIIX_STR_PREFIX + "." + qmstr_key) >= 0:
            new_line_str = linestr.replace(
                QMIIX_STR_PREFIX + "." + qmstr_key, qmstr_key_dict[qmstr_key])
            if show_replace_string:
                print(
                    f'Fount {qmstr_key} in {linestr} replaced with {new_line_str}')


def get_nsstring_key_from_code_and_replace(fname, replace_fname, qmstr_key, replace_key, fail_log_file=open("log.txt", "w")):
    sourcefile = open(fname, mode='r')
    lines = sourcefile.readlines()
    sourcefile.close()
    found = False
    for index, oneline in enumerate(lines):
        # search_keys_in_line(oneline, qmstr_key)
        if oneline.find(QMIIX_STR_PREFIX + "." + qmstr_key) >= 0 and not re.match( f'.*{QMIIX_STR_PREFIX}.{qmstr_key}\w.*', oneline, re.M|re.I):
            found = True
            oneline = oneline.replace(
                QMIIX_STR_PREFIX + "." + qmstr_key, replace_key)
            if show_replace_string:
                print(
                    f'Fount {qmstr_key} in {lines[index]} replace with {oneline}')
        lines[index] = oneline
    if found:
        return lines
    return []
    # targetfile = open(replace_fname, mode='w')
    # targetfile.writelines(lines)
    # sourcefile.close()
    # fail_log_file.close()

show_replace_lines = False
def fix_swift_file_in_filepath(src_dname, dst_dname, keystr, replace_key, do_replace=False):
    fnames = get_swift_file(src_dname)
    fail_log_file = open("log.txt", mode='w')
    key_referenced = False
    for targetfile in fnames:
        replacefile = targetfile.replace(src_dname, dst_dname)
        if show_processing_files:
            print(f'Processing file {targetfile} ...')
        replaced_lines = get_nsstring_key_from_code_and_replace(targetfile, replacefile, keystr, replace_key, fail_log_file=fail_log_file)
        if len(replaced_lines) > 0:
            key_referenced = True
            if show_replace_lines:
                print('Replace lines')
        if do_replace and len(replaced_lines) > 0:
            with open(replacefile, "w") as replace_fd:
                print(f'Replace lines in {replacefile}')
                replace_fd.writelines(replaced_lines)
                replace_fd.close()
            message_fd = open("message.txt", "a")
            print(f'Refactor {keystr} in {targetfile}', file = message_fd)
            message_fd.close()

    fail_log_file.close()
    return key_referenced

def scan_key_dict(src_dname, dst_dname, qmstr_dict :dict):
    empty_key_log = open('empty_key.log', 'w')
    white_lists = ["CONNECTED_ACCOUNTS", "CONNECTED_DEVICES", "ACTIVITY", "TRIGGER", "ACTION", "PLACE_HOLDER_PLEASE_SELECT", 
        "ACTION_CONDITION_AND", "ACTION_CONDITION_OR" , "MIIX_FILTER_BY", "MIIX_SORTED_BY", "ALL", "MIIX_CREATION_DATE", "MIIX_TOTAL_RUNS",
        "SUCCESS", "TRIGGER_ESSENTIALS", "CONFIGURE", "MY_MIIXES", "APP_CONNECTED", "CONDITIONSTATEMENT", "FROM_DATE"]

    for qmstr_key in qmstr_dict:
        white_listed = False
        for whitelist_key in white_lists:
            if whitelist_key == qmstr_key:
                white_listed = True
                break
        if white_listed:
            continue
        key_referenced = fix_swift_file_in_filepath(src_dname, dst_dname, qmstr_key, qmstr_dict[qmstr_key], False)
        if key_referenced:
            print(f'Replace the files with key {qmstr_key} yes or no?')
            for answer in sys.stdin:
                answer = answer.rstrip()
                if answer == 'yes' or answer == 'no' or answer == 'y' or answer == 'n':
                    break
                print(f'Replace the files with key {qmstr_key} yes or no?')
            print(f'Read answer {answer}')
            if answer == "yes" or answer == 'y':
                fix_swift_file_in_filepath(src_dname, dst_dname, qmstr_key, qmstr_dict[qmstr_key], True)
                print(f'Done .................')
        else:
            print(f'Key {qmstr_key} is not referenced in any swift file')
            print(f'{qmstr_key}', file = empty_key_log)
    empty_key_log.close()

def find_item_in_list(item:str, listset : list):
    for oneitem in listset:
        if item == oneitem.rstrip():
            return oneitem
    return None

def remote_empty_key(const_file : str, empty_key_file : str, target_const_file = "QMConstants.swift"):
    class_find_status = "not found"
    with open(empty_key_file, "r") as empty_key_fd:
        empty_key_lines = empty_key_fd.readlines()
        empty_key_fd.close()
    newconst_lines = []
    with open(const_file, "r") as miix_const:
        constlines = miix_const.readlines()
        miix_const.close()
        for index, constline in enumerate(constlines):
            if constline.find(QMIIX_STR_PREFIX) >= 0:
                class_find_status = "found"
            elif class_find_status == "found" and constline.find("}") >= 0:
                class_find_status = "finished"
            if class_find_status == "found" and constline.find(QMIIX_STR_DECLA) >= 0:
                varname, varvalue = get_var_name_and_value(constline, QMIIX_STR_DECLA)
                if find_item_in_list(varname, empty_key_lines):
                    print(f'Found {varname}')
                else:
                    newconst_lines.append(constline)
            else:
                newconst_lines.append(constline)
    with open(target_const_file,"w") as tgt_fd:
        tgt_fd.writelines(newconst_lines)
        tgt_fd.close()


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
I18NSTR_DECLA = "i18n."

show_found_string_key = True

def process_QMIIX_String_class(const_file = "QMConstants.swift", fail_log_file = open("qmiix_string_process_error.log", "w")):
    class_find_status = "not found"
    qmstring_sict = {}
    with open(const_file, "r") as miix_const:
        constlines = miix_const.readlines()
        miix_const.close()
        for index, constline in enumerate(constlines):
            if constline.find(QMIIX_STR_PREFIX) >= 0:
                class_find_status = "found"
            elif class_find_status == "found" and constline.find("}") >= 0:
                class_find_status = "finished"
            if class_find_status == "found" and constline.find(QMIIX_STR_DECLA) >= 0:
                varname, varvalue = get_var_name_and_value(constline, QMIIX_STR_DECLA)
                if (varvalue.find(I18NSTR_DECLA) >= 0):
                    if show_found_string_key:
                        print(f'Found key {varname} value {varvalue}')
                    qmstring_sict[varname] = varvalue
                    # qmstring_sict[varname + FIX_REPLACE_ANSWER_POSTFIX] = "no"
    return qmstring_sict

if __name__ == "__main__" :
    # print('Number of arguments: {}'.format(len(sys.argv)))
    if (len(sys.argv) < 2):
        print('Usage process_csv_string.py csvfile')
        exit(1)
    # print('Argument(s) passed: {}'.format(str(sys.argv)))


    # /Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift
    if len(sys.argv) > 3:
        src_dname = sys.argv[2]
        dst_dname = sys.argv[3]
        # i18ndict = convert_underscore_to_camel_from_i18n(src_dname + "/SwiftGenFiles/outputs/i18n.swift")
        # idd = get_string_id_dictionary(sys.argv[1], i18ndict)
        # fix_swift_file_in_filepath(src_dname, dst_dname, idd)
        qmstr_dict = process_QMIIX_String_class("/Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift")
        message_fd = open("message.txt", "w")
        message_fd.close()
        scan_key_dict(src_dname, dst_dname, qmstr_dict)
        remote_empty_key("/Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift", "empty_key.log", "/Users/admin/projects/qmiix/qmiix-ios-fixstr/Qmiix/QmiixConstants/QMConstants.swift")
