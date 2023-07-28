import requests
import re
import fileinput
import os

URL = "https://pastebin.com/raw/tQ3R7NJq"
OFFSET_LIST = [
    # ... (unchanged) ...
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

    for offset in OFFSET_LIST:
        section = offset["section"]
        keyname = offset["keyname"]
        pattern = rf"\[{section}\][\s\S]*?{keyname}=(\w+)"
        match = re.search(pattern, input_string)

        if match:
            value = match.group(1)
            print(f"Get {offset.get('name')} == {value}")
            offset["value"] = value
        else:
            print(f"!!!!!!!!!!Not Get {offset['name']} !!!!!!!!!!!")

def get_replacement(offset_name, offset_value):
    if offset_name == "OFFSET_LOCAL_ENT":
        if offset_value == "":
            return False
        replace = f"#define {offset_name} ({offset_value}+0x8)"
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

# New function to update the game version
def update_game_version(filepath, new_version):
    version_pattern = r"(//GameVersion=)(.*)"
    replacement = rf"\1{new_version}"
    
    with fileinput.FileInput(filepath, inplace=True, backup='.bak') as file:
        for line in file:
            line = re.sub(version_pattern, replacement, line.rstrip())
            print(line)

    # remove bak
    backup_file_path = filepath + ".bak"
    os.remove(backup_file_path)

if __name__ == "__main__":
    match_values()
    for offset in OFFSET_LIST:
        replace_macro(FILE_PATH, offset["name"], offset["value"])
    update_game_version(FILE_PATH, "v3.0.35.21")
