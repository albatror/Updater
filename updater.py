import re
import configparser
import json
from datetime import datetime
import sys
import requests 
import os

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


def normalize_name(name):
    """Normalizes names by removing common prefixes and making it lowercase."""
    if not name: return ""
    name = str(name).lower()
    # Common aliases
    if name == "localentityhandle": return "localplayerhandle"

    # Strip common prefixes
    prefixes = ['dt_', 'm_', 'cl_', 'c_', 'p_', 'fl_', 'dw']
    # Sort prefixes by length descending to match longest possible prefix first
    prefixes.sort(key=len, reverse=True)

    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                changed = True
                break

    return name.replace("_", "").replace("!", "").replace("-", "").replace(" ", "")

def load_offsets_ini(file_path_or_url):
    """
    Loads offsets from an INI or JSON (Type-2) file (local or URL).
    """
    content = ""
    if file_path_or_url.startswith('http://') or file_path_or_url.startswith('https://'):
        print(f"{ConsoleColors.BLUE}Fetching offsets from URL: {file_path_or_url}{ConsoleColors.RESET}")
        try:
            response = requests.get(file_path_or_url, timeout=10) 
            response.raise_for_status()  
            content = response.text
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "N/A"
            print(f"{ConsoleColors.RED}HTTP error fetching from URL: {file_path_or_url}. Status Code: {status_code}. Error: {e}{ConsoleColors.RESET}")
            return None
        except Exception as e:
            print(f"{ConsoleColors.RED}Error fetching from URL: {e}{ConsoleColors.RESET}")
            return None
    else:
        print(f"{ConsoleColors.BLUE}Loading offsets from local file: {file_path_or_url}{ConsoleColors.RESET}")
        if not os.path.exists(file_path_or_url):
            print(f"{ConsoleColors.RED}Local INI file not found: {file_path_or_url}{ConsoleColors.RESET}")
            return None
        try:
            with open(file_path_or_url, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"{ConsoleColors.RED}Could not read local file: {e}{ConsoleColors.RESET}")
            return None

    config_dict = {}

    # Check for Type-2 JSON
    if '{' in content and ('"Mics"' in content or '"RecvTable"' in content or '"weaponSettings"' in content):
        try:
            json_start = content.find('{')
            json_data = json.loads(content[json_start:])
            print(f"{ConsoleColors.GREEN}Detected Type-2 JSON format.{ConsoleColors.RESET}")

            section_remap = {"Mics": "Miscellaneous", "weaponSettings": "WeaponSettings", "dataMap": "DataMap"}

            for section, data in json_data.items():
                remapped_section = section_remap.get(section, section)
                if isinstance(data, dict):
                    # Check for nested structures (like RecvTable.DT_BaseEntity)
                    is_nested = any(isinstance(v, dict) for v in data.values())
                    if is_nested:
                        for sub_section, sub_data in data.items():
                            full_section = f"{remapped_section}.{sub_section}"
                            if full_section not in config_dict: config_dict[full_section] = {}
                            if isinstance(sub_data, dict):
                                for k, v in sub_data.items():
                                    config_dict[full_section][k] = str(v)
                            else:
                                config_dict[full_section][sub_section] = str(sub_data)
                    else:
                        if remapped_section not in config_dict: config_dict[remapped_section] = {}
                        for k, v in data.items():
                            config_dict[remapped_section][k] = str(v)
                else:
                    if "Miscellaneous" not in config_dict: config_dict["Miscellaneous"] = {}
                    config_dict["Miscellaneous"][remapped_section] = str(data)

            if config_dict:
                return config_dict
        except Exception as e:
            print(f"{ConsoleColors.YELLOW}Type-2 JSON parse attempt failed, trying INI: {e}{ConsoleColors.RESET}")

    # Fallback to INI
    try:
        # Pre-process for weird INI quirks like "[]"
        processed_content = content.replace("\n[]", "\n")
        # Handle sections with spaces like "[Mics] "
        processed_content = re.sub(r'\[\s*(.+?)\s*\]', r'[\1]', processed_content)

        # Handle lines starting with " = " (missing key)
        lines = processed_content.splitlines()
        for i, line in enumerate(lines):
            if re.match(r'^\s*=', line):
                lines[i] = f"MalformedKey_{i}{line}"
        processed_content = "\n".join(lines)

        parser = configparser.ConfigParser(strict=False, interpolation=None)
        parser.read_string(processed_content)

        # Convert to dict for uniform access
        section_remap = {"Mics": "Miscellaneous", "weaponSettings": "WeaponSettings"}
        for section in parser.sections():
            remapped_section = section_remap.get(section, section)
            if remapped_section not in config_dict: config_dict[remapped_section] = {}
            for key, value in parser.items(section):
                config_dict[remapped_section][key] = value
        print(f"{ConsoleColors.GREEN}Successfully parsed as INI.{ConsoleColors.RESET}")
        return config_dict
    except Exception as e:
        print(f"{ConsoleColors.RED}Failed to parse INI: {e}{ConsoleColors.RESET}")
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


def find_offset_in_config(config, section_name, key_name):
    """Finds an offset in the config with fuzzy matching for section and key."""
    if not config: return None

    # Potential sub-section in key_name (e.g., "CPlayer!lastVisibleTime")
    if "!" in key_name or "." in key_name or ">" in key_name:
        parts = re.split(r'[!.\->]+', key_name)
        key_to_try = [key_name, parts[-1]]
    else:
        key_to_try = [key_name]

    for kt in key_to_try:
        normalized_target_section = normalize_name(section_name)
        normalized_target_key = normalize_name(kt)

        # Find potential matching sections (handle cut-off section names)
        matching_sections = []
        for config_section in config:
            norm_config_section = normalize_name(config_section)
            if norm_config_section == normalized_target_section:
                matching_sections.append(config_section)
            elif len(norm_config_section) >= 4 and (normalized_target_section.endswith(norm_config_section) or norm_config_section.endswith(normalized_target_section)):
                matching_sections.append(config_section)
            elif "." in section_name and normalize_name(section_name.split(".")[0]) == norm_config_section:
                matching_sections.append(config_section)

        for cs in matching_sections:
            best_suffix_match = None
            # Try exact match within section
            if kt in config[cs]:
                return config[cs][kt]

            for config_key in config[cs]:
                norm_config_key = normalize_name(config_key)
                if norm_config_key == normalized_target_key:
                    return config[cs][config_key]

                # Suffix matching for cut-off keys
                if len(norm_config_key) >= 3:
                    if normalized_target_key.endswith(norm_config_key) or norm_config_key.endswith(normalized_target_key):
                        best_suffix_match = config[cs][config_key]

            if best_suffix_match:
                return best_suffix_match
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
        # Attempt to find a comment keyword (the first non-whitespace block after "// ")
        keywords = re.findall(r'//\s*(\S+)', line_content)
        
        if keywords and re.match(r"\[", keywords[0]): # Potential offset key like [Section].Key
            # Regex to parse "[Section].Key" or "[Section]->Key" format from the comment keyword
            comment_pattern = re.compile(r'\[(.+?)\][\.->]+(.+)')
            comment_match = comment_pattern.search(keywords[0])
            if comment_match:
                section, keyword = comment_match.group(1), comment_match.group(2)
                value = find_offset_in_config(dump_file_config, section, keyword)

                if value:
                    # Replace the old offset value with the new one from source
                    line_content = re.sub(offset_pattern, value, line_content, count=1)
                    # Update the "updated" date in the comment
                    if date_pattern.search(line_content):
                        line_content = re.sub(date_pattern, "updated " + current_date_str_param, line_content, count=1)
                    else:
                        line_content = line_content.rstrip() + " updated " + current_date_str_param
                else:
                    # Section/key not found in INI, mark for reporting
                    not_found_lines_list.append(original_line)
            else:
                # Comment started with "[" but didn't match the "[Section].Key" pattern.
                unrecognized_lines_list.append(original_line)
        elif not keywords: # No comment, or comment is empty or only whitespace
            # This line has no parsable comment keyword, so keep it as is.
            pass 
        elif keywords[0] == "Date": # Special keyword for overall date
            line_content = f"//Date {current_date_str_param}"
        elif keywords[0] == "GameVersion": # Special keyword for game version
            value = find_offset_in_config(dump_file_config, "Miscellaneous", "GameVersion")
            if value:
                line_content = f"//GameVersion = {value}"
            else:
                not_found_lines_list.append(original_line)
        else: # Comment keyword exists but is not recognized (e.g., not "[Section].Key", "Date", or "GameVersion")
            if line_content.strip(): # Avoid adding completely empty lines as unrecognized
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
        # This case is usually handled before report_results is called, but good for completeness.
        print(ConsoleColors.RED + "Critical error: The updated .h file could not be written." + ConsoleColors.RESET)
        # No further positive message should be printed.
        return

    if not not_found_lines and not unrecognized_lines:
        print(ConsoleColors.GREEN + "Update completed successfully! All recognized lines were processed." + ConsoleColors.RESET)
    else:
        print(ConsoleColors.YELLOW + "Update completed with some issues. Please review the details below:" + ConsoleColors.RESET)

        if not_found_lines:
            print(ConsoleColors.RED + "\nLines Not Found in INI Source:" + ConsoleColors.RESET)
            print("The following lines in your .h file referred to sections/keys or specific values (like GameVersion)")
            print("that were not found in the provided .ini source. These lines were NOT updated:")
            for line in not_found_lines:
                print(ConsoleColors.RED + f"  - {line.strip()}" + ConsoleColors.RESET)

        if unrecognized_lines:
            print(ConsoleColors.YELLOW + "\nUnrecognized Lines in .h File:" + ConsoleColors.RESET)
            print("The following lines in your .h file contained comments or structures that the script")
            print("did not recognize or know how to process. These lines were kept as is:")
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
                return False # Indicates failure / cancellation
            if os.path.exists(user_h_path) and os.path.isfile(user_h_path):
                offset_h_path = user_h_path
                break
            else:
                print(ConsoleColors.RED + f"File not found or not a file: {user_h_path}. Please try again." + ConsoleColors.RESET)
    else:
        print(f"{ConsoleColors.GREEN}Found '{offset_h_path}' in the current directory.{ConsoleColors.RESET}")
    
    offset_ini_path_or_url = None
    while True:
        ini_source_choice = input(f"Update from {ConsoleColors.BOLD}local{ConsoleColors.RESET} 'offsets.ini' or from a {ConsoleColors.BOLD}URL{ConsoleColors.RESET}? (local/url, press Enter to cancel): ").strip().lower()
        if not ini_source_choice:
            print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
            return False

        if ini_source_choice == 'local':
            default_ini_path = 'offsets.ini'
            if os.path.exists(default_ini_path) and os.path.isfile(default_ini_path):
                print(f"{ConsoleColors.GREEN}Found '{default_ini_path}' in the current directory.{ConsoleColors.RESET}")
                offset_ini_path_or_url = default_ini_path
                break
            else:
                print(ConsoleColors.YELLOW + f"'{default_ini_path}' not found in the current directory." + ConsoleColors.RESET)
                user_ini_path = input(f"Enter the full path to 'offsets.ini' or a URL to fetch it from (or press Enter to cancel): ").strip()
                if not user_ini_path:
                    print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
                    return False
                offset_ini_path_or_url = user_ini_path
                break 
        elif ini_source_choice == 'url':
            user_url = input("Please enter the URL for offsets.ini (or press Enter to cancel): ").strip()
            if not user_url:
                print(ConsoleColors.RED + "Operation cancelled by user." + ConsoleColors.RESET)
                return False
            offset_ini_path_or_url = user_url
            break
        else:
            print(ConsoleColors.RED + "Invalid choice. Please type 'local' or 'url'." + ConsoleColors.RESET)

    if not offset_ini_path_or_url: 
        print(ConsoleColors.RED + "Offsets.ini source is required. Aborting." + ConsoleColors.RESET)
        return False

    print(f"\n{ConsoleColors.CYAN}Starting update process...{ConsoleColors.RESET}")
    print(f"Using H file: '{offset_h_path}'")
    print(f"Using INI source: '{offset_ini_path_or_url}'")

    dump_config = load_offsets_ini(offset_ini_path_or_url)
    if dump_config is None:
        print(ConsoleColors.RED + "Failed to load INI data. Aborting update." + ConsoleColors.RESET)
        # report_results([], [], False) # No, this would be confusing as no processing happened
        return False 

    offset_h_original_lines = read_offsets_h(offset_h_path)
    if offset_h_original_lines is None:
        print(ConsoleColors.RED + f"Failed to read H file '{offset_h_path}'. Aborting update." + ConsoleColors.RESET)
        return False 

    updated_lines, not_found, unrecognized = process_offsets_update(offset_h_original_lines, dump_config, date_str)

    h_file_written = False
    if write_updated_offsets_h(offset_h_path, updated_lines):
        # Removed the success message from here; report_results will handle it.
        h_file_written = True
    else:
        # Error message already printed by write_updated_offsets_h
        print(ConsoleColors.RED + f"Update process FAILED to write updated H file '{offset_h_path}'." + ConsoleColors.RESET)
        # No need to return False immediately, let report_results summarize with h_file_written = False

    report_results(not_found, unrecognized, h_file_written)
    
    # The orchestrator's return value indicates overall success/failure of the operation
    if not h_file_written or not_found or unrecognized:
        return False 
    return True 


if __name__ == '__main__':
    success = update_offsets_orchestrator()
    if success:
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.GREEN}Script finished successfully.{ConsoleColors.RESET}")
    else:
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.RED}Script finished with errors or cancellations.{ConsoleColors.RESET}")
