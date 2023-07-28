import re
import requests
import fileinput
import os

url = "https://pastebin.com/raw/tQ3R7NJq"
file_path = "./offsets.h"

# Function to extract GameVersion from the update file
def get_game_version_from_update():
    response = requests.get(url)
    if response.status_code == 200:
        match = re.search(r"GameVersion=V([\d.]+)", response.text)
        if match:
            return match.group(1)
    return None

# Function to update the GameVersion in the offsets.h file
def update_game_version(game_version):
    # Create a backup file explicitly
    backup_file_path = file_path + ".bak"
    with open(file_path, 'r') as f:
        with open(backup_file_path, 'w') as f_backup:
            f_backup.write(f.read())

    pattern = r"//GameVersion=V([\d.]+)"
    replacement = f"//GameVersion=V{game_version}"
    fileinput.FileInput(file_path, inplace=True, backup='').re_sub(pattern, replacement)

    # Remove the backup file
    os.remove(backup_file_path)

# Parse offsets.h to get existing offsets
offset_list = []
with open(file_path) as f:
    for line in f:
        m = re.match(r"#define (\w+) (0x[0-9A-Fa-f]+)", line)
        if m:
            name = m.group(1)
            offset_list.append({"name": name, "keyname": name})

def get_new_offsets():
    response = requests.get(url)  
    new_offsets = {}
    missing_offsets = []
    
    if response.status_code == 200:
        for offset in offset_list:
            keyname = offset["keyname"]
            pattern = rf"\w+{keyname}=([\w]+)"
            match = re.search(pattern, response.text)

            if match:
                new_offsets[offset["name"]] = match.group(1)
            else:
                missing_offsets.append(offset["name"])
                
    return new_offsets, missing_offsets

def update_offsets(new_offsets):
    # Create a backup file explicitly
    backup_file_path = file_path + ".bak"
    with open(file_path, 'r') as f:
        with open(backup_file_path, 'w') as f_backup:
            f_backup.write(f.read())

    for name, value in new_offsets.items():
        pattern = rf"#define {name}\s+([^\r\n]*)"
        replacement = f"#define {name} {value}"
        fileinput.FileInput(file_path, inplace=True, backup='').re_sub(pattern, replacement)

    # Remove the backup file
    os.remove(backup_file_path)

if __name__ == "__main__":
    # Get the GameVersion from the update file
    game_version_from_update = get_game_version_from_update()

    if game_version_from_update:
        # Update the GameVersion in the offsets.h file
        update_game_version(game_version_from_update)
        print(f"GameVersion updated to V{game_version_from_update}")

    new_offsets, missing_offsets = get_new_offsets()
    
    if missing_offsets:
        with open("Errors_offsets", "w") as f:
            f.write("\n".join(missing_offsets))
            
    update_offsets(new_offsets)
