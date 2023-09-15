import requests
import re
import fileinput
import os

URL = "https://pastebin.com/raw/tQ3R7NJq"

# Define the offsets in a list of dictionaries as in your original code.
OFFSET_LIST = OFFSET_LIST = [
    {"name": "OFFSET_LOCAL_ENT", "section": "Miscellaneous", "keyname": "LocalPlayer", "value": ""},
    {"name": "OFFSET_INPUTSYSTEM", "section": "Miscellaneous", "keyname": "InputSystem", "value": ""},
    {"name": "OFFSET_GLOBALVAR", "section": "Miscellaneous", "keyname": "GlobalVars", "value": ""},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": ""},
    {"name": "OFFSET_LEVEL_NAME", "section": "Miscellaneous", "keyname": "LevelName", "value": ""},
    {"name": "OFFSET_STUDIOHDR", "section": "Miscellaneous", "keyname": "CBaseAnimating!m_pStudioHdr", "value": ""},
    {"name": "OFFSET_CAMERAPOS", "section": "Miscellaneous", "keyname": "CPlayer!camera_origin", "value": ""},
    {"name": "OFFSET_MATRIX", "section": "Miscellaneous", "keyname": "ViewMatrix", "value": ""},
    {"name": "OFFSET_RENDER", "section": "Miscellaneous", "keyname": "ViewRender", "value": ""},
    {"name": "OFFSET_VISIBLE_TIME", "section": "RecvTable.DT_BaseCombatCharacter", "keyname": "CPlayer!lastVisibleTime", "value": ""},
    {"name": "OFFSET_ZOOM_FOV", "section": "RecvTable.DT_WeaponX", "keyname": "m_playerData", "value": ""},
    {"name": "OFFSET_HANG_ON_WALL", "section": "DataMap.C_Player", "keyname": "m_traversalStartTime", "value": ""},
    {"name": "OFFSET_HANG_TIME", "section": "DataMap.C_Player", "keyname": "m_traversalProgress", "value": ""},
    {"name": "OFFSET_ZOOMING", "section": "DataMap.C_Player", "keyname": "m_bZooming", "value": ""},
    {"name": "OFFSET_YAW", "section": "DataMap.C_Player", "keyname": "m_currentFramePlayer.m_ammoPoolCount", "value": ""},
    {"name": "OFFSET_AIMPUNCH", "section": "DataMap.C_Player", "keyname": "m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle", "value": ""},
    #{"name": "OFFSET_VIEWMODEL", "section": "[RecvTable.DT_Player]", "keyname": "m_hViewModels", "value": ""},
    #{"name": "OFFSET_GAMEMODE", "section": "[ConVars]", "keyname": "mp_gamemode", "value": ""},
    {"name": "OFFSET_THIRDPERSON", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_thirdPersonShoulderView", "value": ""},
    #{"name": "OFFSET_TIMESCALE", "section": "[ConVars]", "keyname": "host_timescale", "value": ""},
    {"name": "OFFSET_HEALTH", "section": "[RecvTable.DT_AI_BaseNPC]", "keyname": "m_iHealth", "value": ""},
    {"name": "OFFSET_SHIELD_TYPE", "section": "[RecvTable.DT_AI_BaseNPC]", "keyname": "m_armorType", "value": ""},
    {"name": "OFFSET_LIFE_STATE", "section": "[RecvTable.DT_AI_BaseNPC]", "keyname": "m_lifeState", "value": ""},
    {"name": "OFFSET_BLEED_OUT_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_bleedoutState", "value": ""},
    {"name": "OFFSET_VIEWANGLES", "section": "[RecvTable.DT_Player]", "keyname": "m_ammoPoolCapacity", "value": ""},
    {"name": "OFFSET_BONES", "section": "[RecvTable.DT_BaseAnimating]", "keyname": "m_nForceBone", "value": ""},
    {"name": "OFFSET_TEAM", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iTeamNum", "value": ""},
    {"name": "OFFSET_SHIELD", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealth", "value": ""},
    {"name": "OFFSET_SHIELD_MAX", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealthMax", "value": ""},
    {"name": "OFFSET_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iName", "value": ""},
    {"name": "OFFSET_SIGN_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iSignifierName", "value": ""},
    {"name": "OFFSET_MODEL_NAME", "section": "[DataMap.C_BaseEntity]", "keyname": "m_ModelName", "value": ""},
    {"name": "OFFSET_ORIGIN", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsOrigin", "value": ""},
    {"name": "OFFSET_ABS_VELOCITY", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsVelocity", "value": ""},
    {"name": "OFFSET_THIRDPERSON_SV", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_thirdPersonShoulderView", "value": ""},
    {"name": "OFFSET_OBSERVER_MODE", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_iObserverMode", "value": ""},
    {"name": "OFFSET_OBSERVING_TARGET", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_hObserverTarget", "value": ""},
    {"name": "OFFSET_WEAPON", "section": "[RecvTable.DT_BaseCombatCharacter]", "keyname": "m_latestPrimaryWeapons", "value": ""},
    {"name": "OFFSET_AMMO", "section": "[DataMap.CWeaponX]", "keyname": "m_ammoInClip", "value": ""},
    {"name": "OFFSET_ITEM_ID", "section": "[RecvTable.DT_PropSurvival]", "keyname": "m_customScriptInt", "value": ""},
    {"name": "OFFSET_ITEM_GLOW", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightFunctionBits", "value": ""},
    {"name": "OFFSET_IN_JUMP", "section": "[Buttons]", "keyname": "in_jump", "value": ""},
    {"name": "OFFSET_IN_DUCK", "section": "[Buttons]", "keyname": "in_duck", "value": ""},
    {"name": "OFFSET_BULLET_SPEED", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileSpeed", "value": ""},
    {"name": "OFFSET_BULLET_GRAVITY", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileScale", "value": ""},
]

# Define the path to the output file
FILE_PATH = "./offsets.h"

def read_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None

def match_values():
    input_string = read_webpage(URL)
    if input_string is None:
        return

    # Print the input_string for debugging
    print("Webpage Source:")
    print(input_string)

    for offset in OFFSET_LIST:
        keyname = offset["keyname"]
        pattern = rf"{re.escape(keyname)}=(\w+)"
        print(f"Matching pattern: {pattern}")
        match = re.search(pattern, input_string)

        if match:
            value = match.group(1)
            print(f"Get {offset['name']} == {value}")
            offset["value"] = value
        else:
            print(f"!!!!!!!!!!Not Get {offset['name']} !!!!!!!!!!!")

def get_replacement(offset_name, offset_value):
    if offset_name == "OFFSET_LOCAL_ENT":
        if offset_value == "":
            return False
        return f"#define {offset_name} {offset_value} + 0x8"
    elif offset_name == "OFFSET_YAW":
        return f"#define {offset_name} {offset_value} - 0x8"
    elif offset_name == "OFFSET_BONES":
        return f"#define {offset_name} {offset_value} + 0x48"
    elif offset_name == "OFFSET_VIEWANGLES":
        return f"#define {offset_name} {offset_value} - 0x14"
    elif offset_name == "OFFSET_ZOOM_FOV":
        return f"#define {offset_name} {offset_value} + 0xb8"
    else:
        return f"#define {offset_name} {offset_value}"

def replace_macro(filepath, macro_name, new_value):
    pattern = r"#define\s+" + re.escape(macro_name) + r"\s+([^/\n\r]*)"
    replacement = get_replacement(macro_name, new_value)

    with fileinput.FileInput(filepath, inplace=True, backup='.bak') as file:
        updated = False  # Flag to check if the macro was updated
        for line in file:
            if re.match(pattern, line):
                # If the macro exists, update it
                line = re.sub(pattern, replacement, line.rstrip())
                updated = True
            print(line)

        if not updated:
            # If the macro didn't exist, append it to the end of the file
            print(replacement)

    # Remove the backup file
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

    # Remove the backup file
    backup_file_path = filepath + ".bak"
    os.remove(backup_file_path)

if __name__ == "__main__":
    # Create the 'offsets.h' file if it doesn't exist
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            pass  # This creates an empty file

    match_values()
    for offset in OFFSET_LIST:
        replace_macro(FILE_PATH, offset["name"], offset["value"])
    update_game_version(FILE_PATH, "")
