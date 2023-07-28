import requests
import re
import fileinput
import os

URL = "https://pastebin.com/raw/tQ3R7NJq"
OFFSET_LIST = [
    {"name": "OFFSET_ENTITYLIST", "section": "Miscellaneous", "keyname": "cl_entitylist", "value": "0x1e54dc8"},
    {"name": "OFFSET_LOCAL_ENT", "section": "Globals", "keyname": "AVC_GameMovement", "value": "35670216 + 0x8"},
    {"name": "OFFSET_NAME_LIST", "section": "Miscellaneous", "keyname": "NameList", "value": "0xbe95d60"},
    {"name": "OFFSET_STUDIOHDR", "section": "Miscellaneous", "keyname": "CBaseAnimating!m_pStudioHdr", "value": "0x10e8"},
    {"name": "OFFSET_CAMERAPOS", "section": "Miscellaneous", "keyname": "CPlayer!camera_origin", "value": "0x1f50"},
    {"name": "OFFSET_MATRIX", "section": "Miscellaneous", "keyname": "ViewMatrix", "value": "0x11A350"},
    {"name": "OFFSET_RENDER", "section": "NetworkedStringTables", "keyname": "EffectDispatch", "value": "0x0743dc00 - 0x1F60"},
    {"name": "OFFSET_VISIBLE_TIME", "section": "[RecvTable.DT_BaseCombatCharacter", "keyname": "m_hudInfo_visibilityTestAlwaysPasses", "value": "0x1a6d + 0x3"},
    {"name": "OFFSET_ZOOM", "section": "[DataMap.WeaponPlayerData]", "keyname": "m_curZoomFOV", "value": "0x00b8"},
    {"name": "OFFSET_ZOOM_FOV", "section": "[RecvTable.DT_WeaponX]", "keyname": "m_playerData", "value": "0x16b0 + OFFSET_ZOOM"},
    {"name": "OFFSET_HANG_ON_WALL", "section": "[DataMap.C_Player]", "keyname": "m_traversalStartTime", "value": "0x2b60"},
    {"name": "OFFSET_HANG_TIME", "section": "[DataMap.C_Player]", "keyname": "m_traversalProgress", "value": "0x2b5c"},
    {"name": "OFFSET_ZOOMING", "section": "[DataMap.C_Player]", "keyname": "m_bZooming", "value": "0x1c51"},
    {"name": "OFFSET_YAW", "section": "[DataMap.C_Player]", "keyname": "m_currentFramePlayer.m_ammoPoolCount", "value": "0x22bc - 0x8"},
    {"name": "OFFSET_AIMPUNCH", "section": "[DataMap.C_Player]", "keyname": "m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle", "value": "0x24b8"},
    {"name": "OFFSET_VIEWMODEL", "section": "[DataMap.C_Player]", "keyname": "m_hViewModels", "value": "0x2d80"},
    {"name": "OFFSET_GAMEMODE", "section": "[ConVars]", "keyname": "mp_gamemode", "value": "0x0223d990 + 0x58"},
    {"name": "OFFSET_THIRDPERSON", "section": "[ConVars]", "keyname": "thirdperson_override", "value": "0x01de45d0 + 0x6c"},
    {"name": "OFFSET_TIMESCALE", "section": "[ConVars]", "keyname": "host_timescale", "value": "0x01799bd0"},
    {"name": "OFFSET_HEALTH", "section": "[RecvTable.DT_Player]", "keyname": "m_iHealth", "value": "0x043c"},
    {"name": "OFFSET_SHIELD_TYPE", "section": "[RecvTable.DT_Player]", "keyname": "m_armorType", "value": "0x4654"},
    {"name": "OFFSET_LIFE_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_lifeState", "value": "0x0798"},
    {"name": "OFFSET_BLEED_OUT_STATE", "section": "[RecvTable.DT_Player]", "keyname": "m_bleedoutState", "value": "0x2750"},
    {"name": "OFFSET_VIEWANGLES", "section": "[RecvTable.DT_Player]", "keyname": "m_ammoPoolCapacity", "value": "0x25b4 - 0x14"},
    {"name": "OFFSET_BONES", "section": "[RecvTable.DT_BaseAnimating]", "keyname": "m_nForceBone", "value": "0x0e98 + 0x48"},
    {"name": "OFFSET_TEAM", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iTeamNum", "value": "0x044c"},
    {"name": "OFFSET_SHIELD", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealth", "value": "0x0170"},
    {"name": "OFFSET_SHIELD_MAX", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_shieldHealthMax", "value": "0x0174"},
    {"name": "OFFSET_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iName", "value": "0x0589"},
    {"name": "OFFSET_SIGN_NAME", "section": "[RecvTable.DT_BaseEntity]", "keyname": "m_iSignifierName", "value": "0x0580"},
    {"name": "OFFSET_MODEL_NAME", "section": "[DataMap.C_BaseEntity]", "keyname": "m_ModelName", "value": "0x0030"},
    {"name": "OFFSET_ORIGIN", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsOrigin", "value": "0x014c"},
    {"name": "OFFSET_ABS_VELOCITY", "section": "[DataMap.C_BaseEntity]", "keyname": "m_vecAbsVelocity", "value": "0x0140"},
    {"name": "OFFSET_THIRDPERSON_SV", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_thirdPersonShoulderView", "value": "0x36e8"},
    {"name": "OFFSET_OBSERVER_MODE", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_iObserverMode", "value": "0x34f4"},
    {"name": "OFFSET_OBSERVING_TARGET", "section": "[RecvTable.DT_LocalPlayerExclusive]", "keyname": "m_hObserverTarget", "value": "0x3500"},
    {"name": "OFFSET_WEAPON", "section": "[RecvTable.DT_BaseCombatCharacter]", "keyname": "m_latestPrimaryWeapons", "value":
    {"name": "OFFSET_AMMO", "section": "[DataMap.CWeaponX]", "keyname": "m_ammoInClip", "value": "0x1660"},
    {"name": "OFFSET_ITEM_ID", "section": "[RecvTable.DT_PropSurvival]", "keyname": "m_customScriptInt", "value": "0x1638"},
    {"name": "OFFSET_ITEM_GLOW", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightFunctionBits", "value": "0x02c0"},
    {"name": "OFFSET_IN_JUMP", "section": "[Buttons]", "keyname": "in_jump", "value": "0x0743e5a0"},
    {"name": "OFFSET_IN_DUCK", "section": "[Buttons]", "keyname": "in_duck", "value": "0x0be967c8"},
    {"name": "OFFSET_BULLET_SPEED", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileSpeed", "value": "OFFSET_VISIBLE_TIME + 0x04cc"},  # CWeaponX!m_flProjectileSpeed=0x1f18
    {"name": "OFFSET_BULLET_GRAVITY", "section": "[RecvTable.CWeaponX]", "keyname": "m_flProjectileScale", "value": "OFFSET_VISIBLE_TIME + 0x04d4"},  # CWeaponX!m_flProjectileScale=0x1f20
    {"name": "OFFSET_GLOW_ENABLE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightServerContextID", "value": "0x3C8"},
    {"name": "OFFSET_GLOW_THROUGH_WALLS", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightServerContextID", "value": "0x3D0 + 0x10"},  # Glowing through the walls : Internal features of Apex Legends 2  enabled, 5  disabled->m_highlightServerContextID + 0x10
    {"name": "OFFSET_GLOW_TYPE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightFunctionBits", "value": "0x2C4+ 0x4"},  # [RecvTable.DT_HighlightSettings]->m_highlightFunctionBits + 0x4
    {"name": "OFFSET_GLOW_COLOR1", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x1D0"},  # m_highlightParams + 0x18 : Glow Color R 464
    {"name": "OFFSET_GLOW_COLOR2", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "OFFSET_GLOW_COLOR1 + 0x4"},  # Glow Color G
    {"name": "OFFSET_GLOW_COLOR3", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "OFFSET_GLOW_COLOR1 + 0x8"},  # Glow Color B
    {"name": "OFFSET_GLOW_DISTANCE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x3B4"},  # Extended offsets for Additional Glow Features
    {"name": "OFFSET_GLOW_LIFE_TIME", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x3A4"},  # Extended offsets for Additional Glow Features
    {"name": "OFFSET_GLOW_FADE", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x388"},  # Extended offsets for Additional Glow Features
    {"name": "OFFSET_GLOW_T1", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x262"},  # 16256 = enabled, 0 = disabled
    {"name": "OFFSET_GLOW_T2", "section": "[RecvTable.DT_HighlightSettings]", "keyname": "m_highlightParams", "value": "0x2dc"},  # 1193322764 = enabled, 0 = disabled
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
