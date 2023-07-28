import requests
import re
import fileinput
import os

URL = "https://pastebin.com/raw/tQ3R7NJq"
OFFSET_LIST = [
    {"name": "OFFSET_ENTITYLIST", "section": "Miscellaneous", "keyname": "cl_entitylist", "value": ""},
    {"name": "OFFSET_LOCAL_ENT", "section": "Miscellaneous", "keyname": "LocalPlayer", "value": ""},
    {"name": "OFFSET_INPUTSYSTEM", "section": "Miscellaneous", "keyname": "InputSystem", "value": ""},
    {"name": "OFFSET_GLOBALVAR", "section": "Miscellaneous", "keyname": "GlobalVars", "value": ""},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": ""},
    {"name": "OFFSET_LEVEL_NAME", "section": "Miscellaneous", "keyname": "LevelName", "value": ""},
    {"name": "OFFSET_STUDIOHDR", "section": "Miscellaneous", "keyname": "CBaseAnimating!m_pStudioHdr", "value": ""},
    {"name": "OFFSET_CAMERAPOS", "section": "Miscellaneous", "keyname": "CPlayer!camera_origin", "value": ""},
    {"name": "OFFSET_MATRIX", "section": "ViewMatrix", "keyname": "", "value": ""},
    {"name": "OFFSET_RENDER", "section": "NetworkedStringTables", "keyname": "EffectDispatch", "value": ""},
    {"name": "OFFSET_VISIBLE_TIME", "section": "RecvTable.DT_BaseCombatCharacter", "keyname": "CPlayer!lastVisibleTime", "value": ""},
    {"name": "OFFSET_ZOOM_FOV", "section": "RecvTable.DT_WeaponX", "keyname": "m_playerData", "value": ""},
    {"name": "OFFSET_HANG_ON_WALL", "section": "DataMap.C_Player", "keyname": "m_traversalStartTime", "value": ""},
    {"name": "OFFSET_HANG_TIME", "section": "DataMap.C_Player", "keyname": "m_traversalProgress", "value": ""},
    {"name": "OFFSET_ZOOMING", "section": "DataMap.C_Player", "keyname": "m_bZooming", "value": ""},
    {"name": "OFFSET_YAW", "section": "DataMap.C_Player", "keyname": "m_currentFramePlayer.m_ammoPoolCount", "value": ""},
    {"name": "OFFSET_AIMPUNCH", "section": "DataMap.C_Player", "keyname": "m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle", "value": ""},
        {"name": "OFFSET_ENTITYLIST", "section": "Miscellaneous", "keyname": "cl_entitylist", "value": "0x1e54dc8"},
    {"name": "OFFSET_LOCAL_ENT", "section": "Globals", "keyname": "AVC_GameMovement", "value": "35670216 + 0x8"},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": "0xbe95d60"},
    {"name": "OFFSET_STUDIOHDR", "section": "Miscellaneous", "keyname": "CBaseAnimating!m_pStudioHdr", "value": ""},
    {"name": "OFFSET_CAMERAPOS", "section": "Miscellaneous", "keyname": "CPlayer!camera_origin", "value": ""},
    {"name": "OFFSET_MATRIX", "section": "Miscellaneous", "keyname": "ViewMatrix", "value": ""},
    {"name": "OFFSET_RENDER", "section": "NetworkedStringTables", "keyname": "EffectDispatch", "value": " - 0x1F60"},
    {"name": "OFFSET_VISIBLE_TIME", "section": "[RecvTable.DT_BaseCombatCharacter", "keyname": "m_hudInfo_visibilityTestAlwaysPasses", "value": " + 0x3"},
    {"name": "OFFSET_ZOOM", "section": "[DataMap.WeaponPlayerData]", "keyname": "m_curZoomFOV", "value": ""},
    {"name": "OFFSET_ZOOM_FOV", "section": "[RecvTable.DT_WeaponX]", "keyname": "m_playerData", "value": " + OFFSET_ZOOM"},
    {"name": "OFFSET_HANG_ON_WALL", "section": "[DataMap.C_Player]", "keyname": "m_traversalStartTime", "value": ""},
    {"name": "OFFSET_HANG_TIME", "section": "[DataMap.C_Player]", "keyname": "m_traversalProgress", "value": ""},
    {"name": "OFFSET_ZOOMING", "section": "[DataMap.C_Player]", "keyname": "m_bZooming", "value": ""},
    {"name": "OFFSET_YAW", "section": "[DataMap.C_Player]", "keyname": "m_currentFramePlayer.m_ammoPoolCount", "value": " - 0x8"},
    {"name": "OFFSET_AIMPUNCH", "section": "[DataMap.C_Player]", "keyname": "m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle", "value": ""},
    {"name": "OFFSET_VIEWMODEL", "section": "[DataMap.C_Player]", "keyname": "m_hViewModels", "value": ""},
    {"name": "OFFSET_GAMEMODE", "section": "[ConVars]", "keyname": "mp_gamemode", "value": " + 0x58"},
    {"name": "OFFSET_THIRDPERSON", "section": "[ConVars]", "keyname": "thirdperson_override", "value": " + 0x6c"},
    {"name": "OFFSET_TIMESCALE", "section": "[ConVars]", "keyname": "host_timescale", "value": ""},
    {"name": "OFFSET_HEALTH", "section": "[RecvTable.DT_Player]", "keyname": "m_iHealth", "value": ""},
    {"name": "OFFSET_SHIELD_TYPE", "section": "[RecvTable.DT_Player]", "keyname": "m_armorType", "value": ""},
    {"name": "OFFSET_LIFE_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_lifeState", "value": ""},
    {"name": "OFFSET_BLEED_OUT_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_bleedoutState", "value": ""},
    {"name": "OFFSET_VIEWANGLES", "section": "[RecvTable.DT_Player]", "keyname": "m_ammoPoolCapacity", "value": " - 0x14"},
    {"name": "OFFSET_BONES", "section": "[RecvTable.DT_BaseAnimating]", "keyname": "m_nForceBone", "value": " + 0x48"},
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
    {"name": "OFFSET_BULLET_SPEED", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileSpeed", "value": "OFFSET_VISIBLE_TIME + 0x04cc"},  # CWeaponX!m_flProjectileSpeed=0x1f18
    {"name": "OFFSET_BULLET_GRAVITY", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileScale", "value": "OFFSET_VISIBLE_TIME + 0x04d4"},  # CWeaponX!m_flProjectileScale=0x1f20
    {"name": "OFFSET_GLOW_ENABLE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightServerContextID", "value": ""},
    {"name": "OFFSET_GLOW_THROUGH_WALLS", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightServerContextID", "value": " + 0x10"},  # Glowing through the walls : Internal features of Apex Legends 2  enabled, 5  disabled->m_highlightServerContextID + 0x10
    {"name": "OFFSET_GLOW_TYPE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightFunctionBits", "value": " + 0x4"},  # [RecvTable.DT_HighlightSettings]->m_highlightFunctionBits + 0x4
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
