import re
import requests 
import fileinput
import os

url = "https://pastebin.com/raw/tQ3R7NJq"
file_path = "./offsets.h"

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
    
    for name, value in new_offsets.items():
        pattern = rf"#define {name}\s+([^\r\n]*)"
        replacement = f"#define {name} {value}"
        fileinput.FileInput(file_path, inplace=True, backup='.bak').re_sub(pattern, replacement)
        
    os.remove(file_path + ".bak")
        
if __name__ == "__main__":
    
    new_offsets, missing_offsets = get_new_offsets()
    
    if missing_offsets:
        with open("Errors_offsets", "w") as f:
            f.write("\n".join(missing_offsets))
            
    update_offsets(new_offsets)
