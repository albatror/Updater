import requests
import re
import fileinput
import os

URL = "https://pastebin.com/hzxwmZmH"

# Define the offsets in a list of dictionaries as in your original code.
OFFSET_LIST = [
    #{"name": "GameVersion", "section": "Miscellaneous", "keyname": "GameVersion", "value": ""},
    {"name": "OFFSET_ENTITYLIST", "section": "Miscellaneous", "keyname": "cl_entitylist", "value": ""},    
    {"name": "OFFSET_LOCAL_ENT", "section": "Miscellaneous", "keyname": "LocalPlayer", "value": ""},
    {"name": "OFFSET_INPUTSYSTEM", "section": "Miscellaneous", "keyname": "InputSystem", "value": ""},
    {"name": "OFFSET_GLOBALVAR", "section": "Miscellaneous", "keyname": "GlobalVars", "value": ""},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": ""},
    {"name": "OFFSET_LEVEL_NAME", "section": "Miscellaneous", "keyname": "LevelName", "value": ""},
    {"name": "OFFSET_STUDIOHDR", "section": "Miscellaneous", "keyname": "CBaseAnimating!m_pStudioHdr", "value": ""},
    {"name": "OFFSET_CAMERAPOS", "section": "Miscellaneous", "keyname": "CPlayer!camera_origin", "value": ""},
    {"name": "OFFSET_MATRIX", "section": "Miscellaneous", "keyname": "ViewMatrix", "value": ""},
    {"name": "OFFSET_RENDER", "section": "Miscellaneous", "keyname": "ViewRender", "value": ""},
    {"name": "OFFSET_ZOOM_FOV", "section": "RecvTable.DT_WeaponX", "keyname": "m_playerData", "value": ""},
    {"name": "OFFSET_ZOOMING", "section": "DataMap.C_Player", "keyname": "m_bZooming", "value": ""},
    {"name": "OFFSET_YAW", "section": "DataMap.C_Player", "keyname": "m_currentFramePlayer.m_ammoPoolCount", "value": ""},
    {"name": "OFFSET_AIMPUNCH", "section": "DataMap.C_Player", "keyname": "m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle", "value": ""},
    {"name": "OFFSET_THIRDPERSON", "section": "[ConVars]", "keyname": "thirdperson_override", "value": ""},
    {"name": "OFFSET_TIMESCALE", "section": "[ConVars]", "keyname": "host_timescale", "value": ""},
    {"name": "OFFSET_HEALTH", "section": "[RecvTable.DT_AI_BaseNPC]", "keyname": "m_iHealth", "value": ""},
    {"name": "OFFSET_ARMORTYPE", "section": "[RecvTable.DT_Player]", "keyname": "m_armorType", "value": ""},
    {"name": "OFFSET_LIFE_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_lifeState", "value": ""},
    {"name": "OFFSET_BLEED_OUT_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_bleedoutState", "value": ""},
    {"name": "OFFSET_VIEWANGLES", "section": "[RecvTable.DT_Player]", "keyname": "m_ammoPoolCapacity", "value": ""},
    {"name": "OFFSET_BONES", "section": "[RecvTable.DT_BaseAnimating]", "keyname": "m_nForceBone", "value": ""},
    {"name": "OFFSET_TEAM", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iTeamNum", "value": ""},
    {"name": "OFFSET_SHIELD", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealth", "value": ""},
    {"name": "OFFSET_MAXSHIELD", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealthMax", "value": ""},
    {"name": "OFFSET_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iName", "value": ""},
    {"name": "OFFSET_SIGN_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iSignifierName", "value": ""},
    {"name": "OFFSET_ABS_VELOCITY", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsVelocity", "value": ""},
    {"name": "OFFSET_THIRDPERSON_SV", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_thirdPersonShoulderView", "value": ""},
    {"name": "OFFSET_OBSERVER_MODE", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_iObserverMode", "value": ""},
    {"name": "OFFSET_OBSERVING_TARGET", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_hObserverTarget", "value": ""},
    {"name": "OFFSET_WEAPON", "section": "[RecvTable.DT_BaseCombatCharacter]", "keyname": "m_latestPrimaryWeapons", "value": ""},
    {"name": "OFFSET_AMMO", "section": "[DataMap.CWeaponX]", "keyname": "m_ammoInClip", "value": ""},
    {"name": "OFFSET_ITEM_ID", "section": "[RecvTable.DT_PropSurvival]", "keyname": "m_customScriptInt", "value": ""},
    {"name": "OFFSET_IN_JUMP", "section": "[Buttons]", "keyname": "in_jump", "value": ""},
    {"name": "OFFSET_IN_DUCK", "section": "[Buttons]", "keyname": "in_duck", "value": ""},
    {"name": "OFFSET_FLAGS", "section": "[RecvTable.DT_Player]", "keyname": "m_fFlags", "value": ""},
    {"name": "OFFSET_IN_FORWARD", "section": "[Buttons]", "keyname": "in_forward", "value": ""},
    {"name": "OFFSET_m_grappleAttached", "section": "[DataMap.GrappleData]", "keyname": "m_grappleAttached", "value": ""},
    {"name": "OFFSET_m_grappleActivateTime", "section": "[DataMap.GrappleData]", "keyname": "m_grappleActivateTime", "value": ""},
    {"name": "OFFSET_TIME_BASE", "section": "[DataMap.C_Player]", "keyname": "m_currentFramePlayer.timeBase", "value": ""},
    {"name": "OFFSET_TRAVERSAL_STARTTIME", "section": "[DataMap.C_Player]", "keyname": "m_traversalStartTime", "value": ""},
    {"name": "OFFSET_TRAVERSAL_PROGRESS", "section": "[DataMap.C_Player]", "keyname": "m_traversalProgress", "value": ""},
    {"name": "OFFSET_WALL_RUN_START_TIME", "section": "[DataMap.C_Player]", "keyname": "m_wallRunStartTime", "value": ""},
    {"name": "OFFSET_WALL_RUN_CLEAR_TIME", "section": "[DataMap.C_Player]", "keyname": "m_wallRunClearTime", "value": ""},
    {"name": "OFFSET_SKYDIVE_STATE", "section": "[DataMap.C_Player]", "keyname": "m_skydiveState", "value": ""},
    #{"name": "OFFSET_HANG_ON_WALL", "section": "DataMap.C_Player", "keyname": "m_traversalStartTime", "value": ""},
    #{"name": "OFFSET_HANG_TIME", "section": "DataMap.C_Player", "keyname": "m_traversalProgress", "value": ""},
    #{"name": "OFFSET_VIEWMODEL", "section": "[RecvTable.DT_Player]", "keyname": "m_hViewModels", "value": ""},
    #{"name": "OFFSET_GAMEMODE", "section": "[ConVars]", "keyname": "mp_gamemode", "value": ""},
    #{"name": "OFFSET_MODEL_NAME", "section": "[DataMap.C_BaseEntity]", "keyname": "m_ModelName", "value": ""},
    #{"name": "OFFSET_ITEM_GLOW", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightFunctionBits", "value": ""},
    #{"name": "OFFSET_m_grapple", "section": "[RecvTable.DT_Player]", "keyname": "m_grapple=", "value": ""},
    #{"name": "OFFSET_ORIGIN", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsOrigin", "value": ""},
    #{"name": "OFFSET_VISIBLE_TIME", "section": "WeaponSettingsMeta", "keyname": "base", "value": ""},
    #{"name": "OFFSET_BULLET_SPEED", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileSpeed", "value": ""},
    #{"name": "OFFSET_BULLET_GRAVITY", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileScale", "value": ""},
]

# Define additional operations for specific offsets
offset_operations = {
    "OFFSET_THIRDPERSON": "+ 0x6c",
    "OFFSET_YAW": "- 0x8",
    "OFFSET_BONES": "+ 0x48",
    "OFFSET_VIEWANGLES": "- 0x14",
    "OFFSET_ZOOM_FOV": "+ 0xb8",
}

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

    current_section = ""
    for offset in OFFSET_LIST:
        keyname = offset["keyname"]
        section = offset["section"]
        pattern = rf"{re.escape(keyname)}\s*=\s*0x([0-9A-Fa-f]+)"
        match = re.search(pattern, input_string, re.IGNORECASE)

        if match and section in input_string:
            value = match.group(1)
            offset["value"] = f"0x{value}"  # Ensure the value is in the correct format
        else:
            print(f"Unable to find value for key: {keyname} in section: {section}")

def write_offsets_to_file(filepath):
    with open(filepath, 'w') as f:
        # Write the GameVersion definition
        f.write("#define VERSION STEAM\n")
        f.write("\n#if VERSION == STEAM\n")
        f.write("\n")

        # Write the OFFSET definitions
        for offset in OFFSET_LIST:
            # Check if an operation is defined for this offset
            operation = offset_operations.get(offset["name"], "")
            offset_value = f"{offset['value']} {operation}".replace("(", "").replace(")", "")  # Remove parentheses
            offset_line = f"#define {offset['name']} {offset_value}\n"
            f.write(offset_line.rstrip() + '\n')  # Remove trailing spaces and add a blank line after each #define statement
            f.write("\n")  # Add a blank line after each #define statement
        
        ###################################################################################        
        # Write the OFFSETS that need to be changed manually and write the closing #endif #
        ###################################################################################
        f.write("\n")
        f.write("// OFFSETS that need to be changed manually\n")
        f.write("#define OFFSET_ORIGIN  0x017c\n")
        f.write("#define OFFSET_ITEM_GLOW  0x0294\n")
        f.write("#define OFFSET_VISIBLE_TIME  0x19b0\n")
        f.write("#define OFFSET_m_grapple  0x2ca8\n")
        f.write("#define OFFSET_CURRENT_FRAME OFFSET_GLOBALVAR + 0x0008\n")       
        f.write("#define OFFSET_BREATH_ANGLES  OFFSET_VIEWANGLES - 0x10\n")
        f.write("#define OFFSET_BULLET_SPEED  OFFSET_VISIBLE_TIME + 0x04d4 //0x1f6c //0x1aa0 + 0x04cc // WeaponSettingsMeta.base + WeaponSettings.projectile_launch_speed\n")
        f.write("#define OFFSET_BULLET_SCALE  OFFSET_VISIBLE_TIME + 0x04dc //0x1f74 //0x1aa0 + 0x04d4 // WeaponSettingsMeta.base + WeaponSettings.projectile_gravity_scale\n")
        f.write("#define OFFSET_GLOW_T1  0x292 //16256 = enabled, 0 = disabled\n")
        f.write("#define OFFSET_GLOW_T2  0x30c //1193322764 = enabled, 0 = disabled\n")
        f.write("#define OFFSET_GLOW_ENABLE  0x02cc //0x3c8 //7 = enabled, 2 = disabled [RecvTable.DT_HighlightSettings] -> m_highlightServerContextID + 0x8\n")
        f.write("#define OFFSET_GLOW_THROUGH_WALLS  0x02d4 //2 = enabled, 5 = disabled [RecvTable.DT_HighlightSettings] -> m_highlightServerContextID + 0x10\n") 
        f.write("#define GLOW_TYPE  0x2c4 + 0x30\n")
        f.write("#define GLOW_COLOR_R  0x200\n")
        f.write("#define GLOW_COLOR_G  GLOW_COLOR_R + 0x04\n")
        f.write("#define GLOW_COLOR_B  GLOW_COLOR_G + 0x04\n")
        f.write("\n")
        f.write("#endif\n")
        
# URL from user at start - if no link, it will take the original url (on top)
def get_user_url():
    user_url = input("Entrez l'adresse URL (ou appuyez sur Entrée pour utiliser la valeur par défaut): ").strip()
    if user_url:
        return user_url
    else:
        return URL

if __name__ == "__main__":
    # Define the path to the output file
    FILE_PATH = "./offsets.h"

    # Create a backup of the existing offsets.h file
    backup_file_path = FILE_PATH + ".bak"
    if os.path.exists(FILE_PATH):
        os.rename(FILE_PATH, backup_file_path)

    # Run the matching function to get the values and write them to the file
    match_values()

    # Write the #define OFFSET lines to the offsets.h file
    write_offsets_to_file(FILE_PATH)
