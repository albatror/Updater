import re
import configparser
from datetime import datetime
import sys
import requests 
import os
import json

class ConsoleColors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'


current_date = datetime.now()
date_str = current_date.strftime("%Y/%m/%d")


def load_offsets_data(file_path_or_url):
    """
    Loads offsets from an INI or JSON file (local or URL).
    Returns a dictionary of offsets.
    """
    content = ""
    if file_path_or_url.startswith('http://') or file_path_or_url.startswith('https://'):
        try:
            response = requests.get(file_path_or_url, timeout=10) 
            response.raise_for_status()  
            content = response.text
        except Exception as e:
            print(f"{ConsoleColors.RED}Error fetching from URL: {file_path_or_url}. Error: {e}{ConsoleColors.RESET}")
            return None
    else:
        try:
            with open(file_path_or_url, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"{ConsoleColors.RED}Error loading local file: {file_path_or_url}. Error: {e}{ConsoleColors.RESET}")
            return None

    # Try parsing as INI first
    parser = configparser.ConfigParser(strict=False)
    try:
        parser.read_string(content)
        if parser.sections():
            print(f"{ConsoleColors.GREEN}Parsed as INI format.{ConsoleColors.RESET}")
            return {section: {k.lower(): v for k, v in parser.items(section)} for section in parser.sections()}
    except Exception:
        pass

    # If not INI or parsing failed, try JSON (Type-2 format with header)
    try:
        json_start = content.find('{')
        if json_start != -1:
            json_content = content[json_start:]
            data = json.loads(json_content)
            print(f"{ConsoleColors.GREEN}Parsed as JSON format.{ConsoleColors.RESET}")

            # Remap/Flatten Type-2 data
            result = {}
            for key, value in data.items():
                section_name = key
                # Remap specific top-level keys
                if key == "Mics":
                    section_name = "Miscellaneous"
                elif key == "weaponSettings":
                    section_name = "WeaponSettings"

                if isinstance(value, dict):
                    # Check if it's a nested table structure like RecvTable or DataMap
                    has_sub_dicts = any(isinstance(v, dict) for v in value.values())
                    if has_sub_dicts:
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                # Flatten to "Section.SubSection"
                                flattened_name = f"{section_name}.{sub_key}"
                                result[flattened_name] = {k.lower(): v for k, v in sub_value.items()}
                            else:
                                if section_name not in result: result[section_name] = {}
                                result[section_name][sub_key.lower()] = sub_value
                    else:
                        result[section_name] = {k.lower(): v for k, v in value.items()}
                else:
                    # Flat key-value pairs
                    if "Miscellaneous" not in result: result["Miscellaneous"] = {}
                    result["Miscellaneous"][key.lower()] = value
            return result
    except Exception as e:
        print(f"{ConsoleColors.RED}Failed to parse data as either INI or JSON. Error: {e}{ConsoleColors.RESET}")

    return None


def read_offsets_h(file_path):
    """Reads the offsets.h file and returns its content as a list of lines."""
    try:
        with open(file_path, 'r') as head_file:
            return head_file.read().splitlines()
    except FileNotFoundError:
        print(ConsoleColors.RED + f"Error: File not found {file_path}" + ConsoleColors.RESET)
        return None
    except Exception as e:
        print(ConsoleColors.RED + f"An error occurred while reading {file_path}: {e}" + ConsoleColors.RESET)
        return None


def normalize_name(s):
    """Normalizes names for fuzzy matching."""
    # Split by dots to handle Section.SubSection
    parts = s.split('.')
    norm_parts = []
    for part in parts:
        # Lowercase and remove all non-alphanumeric characters
        p_norm = re.sub(r'[^a-z0-9]', '', part.lower())
        # Remove common prefixes
        prefixes = ["cplayer", "cweaponx", "cbaseanimating", "datamap", "recvtable", "dt", "cl", "fl", "m", "c", "p"]
        while True:
            matched = False
            for p in prefixes:
                if p_norm.startswith(p) and len(p_norm) > len(p):
                    p_norm = p_norm[len(p):]
                    matched = True
                    break
            if not matched:
                break
        norm_parts.append(p_norm)
    return "".join(norm_parts)


def fuzzy_get(data, section, keyword):
    """Tries to get a value with fuzzy matching for section and keyword."""
    if not data:
        return None

    # Aliases for keys that changed names significantly
    ALIASES = {
        "localentityhandle": "localplayerhandle",
        "cl_entitylist": "entitylist",
    }

    # 1. Try exact/case-insensitive match for section
    section_data = None
    for s in data:
        if s.lower() == section.lower():
            section_data = data[s]
            break

    # 2. If not found, try fuzzy match for section
    if section_data is None:
        norm_section = normalize_name(section)
        for s in data:
            if normalize_name(s) == norm_section:
                section_data = data[s]
                break

    if section_data:
        keyword_lower = keyword.lower()
        # 1. Check aliases
        if keyword_lower in ALIASES:
            target = ALIASES[keyword_lower]
            if target in section_data:
                return section_data[target]
            # Also check for alias in lowercased form in data
            for k in section_data:
                if k.lower() == target.lower():
                    return section_data[k]

        # 2. Exact match in section
        if keyword_lower in section_data:
            return section_data[keyword_lower]

        # 3. Fuzzy match keyword within section
        norm_keyword = normalize_name(keyword_lower)
        for k, v in section_data.items():
            if normalize_name(k) == norm_keyword:
                return v

    # 4. Global search as last resort if not found in section
    norm_keyword = normalize_name(keyword)
    # Prioritize matching sections (e.g. if we are looking for RecvTable, stay in RecvTable.*)
    for s_name, s_data in data.items():
        if section.split('.')[0].lower() in s_name.lower():
            for k, v in s_data.items():
                if normalize_name(k) == norm_keyword:
                    return v

    # Even wider global search
    for s_name, s_data in data.items():
        for k, v in s_data.items():
            if normalize_name(k) == norm_keyword:
                return v

    return None


def process_offsets_update(offset_h_lines, dump_file_config, current_date_str_param):
    """
    Processes the offset_h lines and updates them based on dump_file_config.
    Returns a tuple: (updated_h_lines, not_found_lines, unrecognized_lines).
    """
    updated_lines = []
    not_found_lines_list = []
    unrecognized_lines_list = []
    
    # Regex to find hexadecimal offset values (e.g., 0x123ABC)
    offset_pattern = re.compile(r'0x[\dA-Fa-f]+')
    # Regex to find "updated" date comments (e.g., updated 2023/01/01)
    date_pattern = re.compile(r'updated (\d{1,4}/\d{1,4}/\d{1,4})')

    for line_content in offset_h_lines:
        original_line = line_content 
        # Attempt to find a comment keyword (non-whitespace blocks after "// ")
        keywords = re.findall(r'//\s*(\S+)', line_content)
        
        if not keywords:
            updated_lines.append(line_content)
            continue

        processed = False

        # Check for offset tag [Section].Key anywhere in the comment
        for k in keywords:
            comment_pattern = re.compile(r'\[(.+?)\](?:\.|\-\>)(.+)')
            comment_match = comment_pattern.search(k)
            if comment_match:
                section, keyword = comment_match.group(1), comment_match.group(2)
                value = fuzzy_get(dump_file_config, section, keyword)
                if value:
                    # Replace the old offset value with the new one
                    line_content = re.sub(offset_pattern, value, line_content, count=1)
                    # Update the "updated" date in the comment
                    line_content = re.sub(date_pattern, "updated " + current_date_str_param, line_content, count=1)
                    processed = True
                else:
                    not_found_lines_list.append(original_line)
                    processed = True
                break

        if processed:
            updated_lines.append(line_content)
            continue

        # Check for special keywords
        found_special = False
        for k in keywords:
            if k == "Date":
                line_content = f"//Date {current_date_str_param}"
                found_special = True
                break
            elif k == "GameVersion":
                version = fuzzy_get(dump_file_config, 'Miscellaneous', 'GameVersion')
                if version:
                    line_content = f"//GameVersion = {version}"
                else:
                    # Try global search for version
                    version = fuzzy_get(dump_file_config, '', 'GameVersion')
                    if version:
                        line_content = f"//GameVersion = {version}"
                    else:
                        not_found_lines_list.append(original_line)
                found_special = True
                break

        if found_special:
            updated_lines.append(line_content)
        else:
            if line_content.strip() and not line_content.startswith("#include"):
                unrecognized_lines_list.append(original_line)
            updated_lines.append(line_content)
        
    return updated_lines, not_found_lines_list, unrecognized_lines_list


def write_updated_offsets_h(file_path, updated_h_lines):
    """Writes the updated lines back to the offsets.h file."""
    try:
        with open(file_path, 'w') as head_file:
            head_file.write('\n'.join(updated_h_lines) + '\n') 
        return True
    except Exception as e:
        print(ConsoleColors.RED + f"An error occurred while writing to {file_path}: {e}" + ConsoleColors.RESET)
        return False


def report_results(not_found_lines, unrecognized_lines, h_file_written_successfully):
    """Prints a summary of the update process, including any issues."""
    print(f"\n--- {ConsoleColors.BOLD}Update Report{ConsoleColors.RESET} ---")

    if not h_file_written_successfully:
        print(ConsoleColors.RED + "Critical error: The updated .h file could not be written." + ConsoleColors.RESET)
        return

    if not not_found_lines and not unrecognized_lines:
        print(ConsoleColors.GREEN + "Update completed successfully! All recognized lines were processed." + ConsoleColors.RESET)
    else:
        print(ConsoleColors.YELLOW + "Update completed with some issues. Please review the details below:" + ConsoleColors.RESET)

        if not_found_lines:
            print(ConsoleColors.RED + f"\nLines Not Found in Source ({len(not_found_lines)}):" + ConsoleColors.RESET)
            for line in not_found_lines:
                print(ConsoleColors.RED + f"  - {line.strip()}" + ConsoleColors.RESET)

        if unrecognized_lines:
            print(ConsoleColors.YELLOW + f"\nUnrecognized Lines in .h File ({len(unrecognized_lines)}):" + ConsoleColors.RESET)
            for line in unrecognized_lines:
                print(ConsoleColors.YELLOW + f"  - {line.strip()}" + ConsoleColors.RESET)
    print("----------------------")


def update_offsets_orchestrator():
    """
    Orchestrates the offset update process using helper functions, with interactive input.
    """
    global date_str 

    offset_h_path = 'offsets.h'
    if not os.path.exists(offset_h_path):
        while True:
            print(ConsoleColors.YELLOW + f"'{offset_h_path}' not found in the current directory." + ConsoleColors.RESET)
            user_h_path = input(f"Please enter the full path to your offsets.h file (or press Enter to cancel): ").strip()
            if not user_h_path:
                print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
                return False
            if os.path.exists(user_h_path) and os.path.isfile(user_h_path):
                offset_h_path = user_h_path
                break
            else:
                print(ConsoleColors.RED + f"File not found or not a file: {user_h_path}. Please try again." + ConsoleColors.RESET)
    else:
        print(f"{ConsoleColors.GREEN}Found '{offset_h_path}' in the current directory.{ConsoleColors.RESET}")
    
    offset_ini_path_or_url = None
    while True:
        ini_source_choice = input(f"Update from {ConsoleColors.BOLD}local{ConsoleColors.RESET} file or from a {ConsoleColors.BOLD}URL{ConsoleColors.RESET}? (local/url, press Enter to cancel): ").strip().lower()
        if not ini_source_choice:
            print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
            return False

        if ini_source_choice == 'local':
            default_ini_path = 'offsets.ini'
            if os.path.exists(default_ini_path) and os.path.isfile(default_ini_path):
                print(f"{ConsoleColors.GREEN}Found '{default_ini_path}' in the current directory.{ConsoleColors.RESET}")
                use_default = input(f"Use '{default_ini_path}'? (y/n, press Enter for y): ").strip().lower()
                if not use_default or use_default == 'y':
                    offset_ini_path_or_url = default_ini_path
                    break

            user_ini_path = input(f"Enter the full path to your offsets file (or press Enter to cancel): ").strip()
            if not user_ini_path:
                print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
                return False
            offset_ini_path_or_url = user_ini_path
            break
        elif ini_source_choice == 'url':
            user_url = input("Please enter the URL for the offsets file (or press Enter to cancel): ").strip()
            if not user_url:
                print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
                return False
            offset_ini_path_or_url = user_url
            break
        else:
            print(ConsoleColors.RED + "Invalid choice. Please type 'local' or 'url'." + ConsoleColors.RESET)

    if not offset_ini_path_or_url: 
        print(ConsoleColors.RED + "Offset source is required. Aborting." + ConsoleColors.RESET)
        return False

    print(f"\n{ConsoleColors.CYAN}Starting update process...{ConsoleColors.RESET}")
    print(f"Using H file: '{offset_h_path}'")
    print(f"Using source: '{offset_ini_path_or_url}'")

    dump_data = load_offsets_data(offset_ini_path_or_url)
    if dump_data is None:
        print(ConsoleColors.RED + "Failed to load offset data. Aborting update." + ConsoleColors.RESET)
        return False 

    offset_h_original_lines = read_offsets_h(offset_h_path)
    if offset_h_original_lines is None:
        print(ConsoleColors.RED + f"Failed to read H file '{offset_h_path}'. Aborting update." + ConsoleColors.RESET)
        return False 

    updated_lines, not_found, unrecognized = process_offsets_update(offset_h_original_lines, dump_data, date_str)

    h_file_written = False
    if write_updated_offsets_h(offset_h_path, updated_lines):
        h_file_written = True
    else:
        print(ConsoleColors.RED + f"Update process FAILED to write updated H file '{offset_h_path}'." + ConsoleColors.RESET)

    report_results(not_found, unrecognized, h_file_written)
    
    if not h_file_written or (not_found and len(not_found) > 30): # Allow some not found
        return False 
    return True 


if __name__ == '__main__':
    success = update_offsets_orchestrator()
    if success:
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.GREEN}Script finished successfully.{ConsoleColors.RESET}")
    else:
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.RED}Script finished with errors or cancellations.{ConsoleColors.RESET}")
