import requests
import re
import fileinput
import os

URL = "https://pastebin.com/raw/tQ3R7NJq"
OFFSET_LIST = [
    {"name": "OFFSET_ENTITYLIST", "section": "Miscellaneous", "keyname": "cl_entitylist", "value": ""},
    {"name": "OFFSET_LOCAL_ENT", "section": "Globals", "keyname": ".?AVC_GameMovement@@", "value": ""},
    {"name": "OFFSET_LOCAL_ENT", "section": "Miscellaneous", "keyname": "LocalPlayer", "value": ""},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": ""},
]
FILE_PATH = "./offsets.h"


def read_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching webpage: {e}")
        return None


def match_values():
    input_string = read_webpage(URL)
    if input_string is None:
        return

    false_count = 0
    success_count = 0
    false_list = []

    for offset in OFFSET_LIST:
        section = offset["section"]
        keyname = offset["keyname"]
        pattern = rf"\[{section}\][\s\S]*?{keyname}=(\w+)"
        match = re.search(pattern, input_string)

        if match:
            success_count += 1
            value = match.group(1)
            print(f"Get {offset.get('name')} == {value}")
            offset["value"] = value
        else:
            false_count += 1
            false_list.append(offset.get("name"))
            print(f"!!!!!!!!!!Not Get {offset['name']} !!!!!!!!!!!")

    print()
    print("====================================================================")
    print("Debug")
    print("Success:", success_count)
    print("False:", false_count)
    print("=================================")

    for false_name in false_list:
        print(false_name)


def get_replacement(offset_name, offset_value):
    if offset_name == "OFFSET_LOCAL_ENT":
        if offset_value == "":
            return False
        replace = f"#define {offset_name} ({offset_value}+0x8)"
        # do action for some specific offset
    else:
        replace = f"#define {offset_name} {offset_value}"

    return replace


def replace_macro(filepath, macro_name, new_value):
    pattern = r"#define\s+" + re.escape(macro_name) + r"\s+([^/\n\r]*)"
    replacement = get_replacement(macro_name, new_value)

    with fileinput.FileInput(filepath, inplace=True, backup='.bak') as file:
        for line in file:
            line = re.sub(pattern, replacement, line.rstrip())
            print(line)

    # remove bak
    backup_file_path = filepath + ".bak"
    os.remove(backup_file_path)


if __name__ == "__main__":
    match_values()
    for offset in OFFSET_LIST:
        replace_macro(FILE_PATH, offset["name"], offset["value"])
