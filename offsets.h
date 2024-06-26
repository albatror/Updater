#define GameVersion v3.0.72.12 //[Miscellaneous].GameVersion 2024/06/26
#define OFFSET_ENTITYLIST 0x1ef7c38 //[Miscellaneous].cl_entitylist updated 2024/06/26
#define OFFSET_LOCAL_ENT 0x22b0328 //[Miscellaneous].LocalPlayer updated 2024/06/26
#define OFFSET_NAME_LIST 0xd2e21e0 //[Miscellaneous].NameList updated 2024/04/22
#define OFFSET_GLOBAL_VARS 0x17e8830 //[Miscellaneous].GlobalVars updated 2024/06/26
 
#define OFFSET_LEVELNAME 0x17e8d34 //[Miscellaneous].LevelName updated 2024/06/26
#define OFFSET_CLIENTSTATE OFFSET_LEVELNAME - 0x1c0 //ClientState  ClientState = LevelName - 0x1C0  //updated 1/10/2024
//#define OFFSET_CLIENTSTATE 0x16d68f0
#define OFFSET_SIGNONSTATE OFFSET_CLIENTSTATE + 0xAC //SignonState   ( ClientState + 0xAC)  //updated 1/10/2024
//#define OFFSET_SIGNONSTATE OFFSET_CLIENTSTATE 0x16d699c
#define OFFSET_HOST_MAP 0x017048a0 + 0x58 //[ConVars].host_map + 0x58 updated 2024/06/26
 
#define OFFSET_TEAM 0x0338 //[RecvTable.DT_BaseEntity].m_iTeamNum updated 2024/06/26
#define OFFSET_HEALTH 0x0328 //[RecvTable.DT_Player].m_iHealth updated updated 2024/06/26
#define OFFSET_SHIELD 0x01a0 //[RecvTable.DT_BaseEntity].m_shieldHealth updated 2024/06/26
#define OFFSET_MAXSHIELD 0x01a4 //[RecvTable.DT_BaseEntity].m_shieldHealthMax updated 2024/06/26
#define OFFSET_ARMORTYPE 0x46d4 //[RecvTable.DT_Player].m_armorType updated updated 2024/06/26
#define OFFSET_NAME 0x0481 //[RecvTable.DT_BaseEntity].m_iName updated 2024/06/26
#define OFFSET_SIGN_NAME 0x0478 //[RecvTable.DT_BaseEntity].m_iSignifierName updated 2024/06/26
#define OFFSET_ABS_VELOCITY 0x0170 //[DataMap.C_BaseEntity].m_vecAbsVelocity updated 2024/06/26
#define OFFSET_VISIBLE_TIME 0x19a0 //[Miscellaneous].CPlayer!lastVisibleTime updated 2024/06/26
#define OFFSET_ZOOMING 0x1be1 //[RecvTable.DT_Player].m_bZooming updated 2024/06/26

#define OFFSET_VIEW_OFFSET 0x00e8 //[DataMap.C_BaseEntity].m_currentFrame.viewOffset updated 2024/06/26
#define OFFSET_ACTIVE_WEAPON 0x18d8 + 0x0058 //[RecvTable.DT_Player].m_inventory + WeaponInventory_Client>activeWeapons updated 2024/06/26

#define OFFSET_SPECTATOR_LIST 0x1ef9c58 //? updated 2024/06/26

#define OFFSET_IN_DUCKSTATE 0x2a70 //[DataMap.C_Player].m_duckState updated 2024/06/26

#define OFFSET_IN_DUCK 0x07542e98 //[Buttons].in_duck updated 2024/06/26
#define OFFSET_TRAVERSAL_PROGRESS 0x2b7c //[DataMap.C_Player].m_traversalProgress updated 2024/06/26
#define OFFSET_TRAVERSAL_STARTTIME 0x2b80 //[DataMap.C_Player].m_traversalStartTime updated 2024/06/26
#define OFFSET_IN_JUMP 0x07542da8 //[Buttons].in_jump updated 2024/06/26
#define OFFSET_IN_TOGGLE_DUCK 0x07542cc8 //[Buttons].in_toggle_duck updated 2024/06/26
 
#define OFFSET_WEAPON_NAME 0x1788 //[RecvTable.DT_WeaponX].m_weaponNameIndex updated 2024/06/26
#define OFFSET_OFF_WEAPON 0x1954 //[DataMap.C_BaseCombatCharacter].m_latestNonOffhandWeapons updated 2024/06/26
#define OFFSET_WALL_RUN_START_TIME 0x3624 //[DataMap.C_Player].m_wallRunStartTime updated 2024/06/26
#define OFFSET_WALL_RUN_CLEAR_TIME 0x3628 //[DataMap.C_Player].m_wallRunClearTime float updated 2024/06/26
#define OFFSET_FLAGS 0x00c8 //[DataMap.C_Player].m_fFlags updated 2024/06/26
#define OFFSET_IN_ATTACK 0x07542ca8 //[Buttons].in_attack updated 2024/06/26
#define OFFSET_IN_ZOOM 0x07542e20 //[Buttons].in_zoom updated 2024/06/26
#define OFFSET_IN_FORWARD 0x07542bd8 //[Buttons].in_forward updated 2024/06/26
 
#define OFFSET_LIFE_STATE 0x0690 //[RecvTable.DT_Player].m_lifeState updated 2024/06/26
#define OFFSET_BLEED_OUT_STATE 0x2770 //[RecvTable.DT_Player].m_bleedoutState updated 2024/06/26
 
#define OFFSET_ORIGIN 0x017c //[DataMap.C_BaseEntity].m_vecAbsOrigin updated 2024/06/26
#define OFFSET_BONES 0x0db0 + 0x48 //[RecvTable.DT_BaseAnimating].m_nForceBone + 0x48 updated 2024/06/26
#define OFFSET_STUDIOHDR 0x1000 //[Miscellaneous].CBaseAnimating!m_pStudioHdr updated 2024/06/26
#define OFFSET_AIMPUNCH 0x2448 //[DataMap.C_Player].m_currentFrameLocalPlayer.m_vecPunchWeapon_Angle updated 2024/06/26
#define OFFSET_CAMERAPOS 0x1ee0 //[Miscellaneous].CPlayer!camera_origin updated 2024/06/26
#define OFFSET_VIEWANGLES 0x2544 - 0x14 //[RecvTable.DT_Player].m_ammoPoolCapacity - 0x14 updated 2024/06/26
#define OFFSET_BREATH_ANGLES OFFSET_VIEWANGLES - 0x10 //updated 01/10/2024
#define OFFSET_OBSERVER_MODE 0x3534 //[RecvTable.DT_LocalPlayerExclusive].m_iObserverMode updated 2024/06/26
#define OFFSET_OBSERVING_TARGET 0x3540 //[RecvTable.DT_LocalPlayerExclusive].m_hObserverTarget updated 2024/06/26
#define OFFSET_IN_USE 0x07542e10 //[Buttons].in_use updated 2024/06/26
 
 
#define OFFSET_MATRIX 0x11a350 //[Miscellaneous].ViewMatrix updated 2024/06/26
#define OFFSET_RENDER 0x7542b80 //[Miscellaneous].ViewRender updated 2024/06/26
 
#define OFFSET_WEAPON 0x1944 //[RecvTable.DT_BaseCombatCharacter].m_latestPrimaryWeapons updated 2024/06/26
#define OFFSET_BULLET_SPEED 0x1eb4 //[Miscellaneous].CWeaponX!m_flProjectileSpeed updated 2024/06/26
#define OFFSET_BULLET_SCALE 0x1ebc //[Miscellaneous].CWeaponX!m_flProjectileScale updated 2024/06/26
#define OFFSET_ZOOM_FOV 0x15e0 + 0x00b8 //[RecvTable.DT_WeaponX].m_playerData + m_curZoomFOV updated 2024/06/26
#define OFFSET_AMMO 0x1564 //[RecvTable.DT_PropSurvival].m_ammoInClip updated 2024/06/26
 
//#define OFFSET_ITEM_GLOW 0x02f0 //m_highlightFunctionBits
#define OFFSET_ITEM_ID 0x1568 //[RecvTable.DT_PropSurvival].m_customScriptInt updated 2024/06/26
#define OFFSET_MODELNAME 0x0030 //[DataMap.C_BaseEntity].m_ModelName updated 2024/06/26
#define OFFSET_M_CUSTOMSCRIPTINT OFFSET_ITEM_ID //[RecvTable.DT_PropSurvival].m_customScriptInt updated 2024/06/26
#define OFFSET_YAW 0x224c - 0x8 //[DataMap.C_Player].m_currentFramePlayer.m_ammoPoolCount - 0x8 updated 2024/06/26
 
//#define OFFSET_GLOW_T1 0x262+ 0x30 //16256 = enabled, 0 = disabled
//#define OFFSET_GLOW_T2 0x2dc+ 0x30 //1193322764 = enabled, 0 = disabled
#define OFFSET_GLOW_ENABLE 0x28C //7 = enabled, 2 = disabled  Script_Highlight_SetCurrentContext //updated 01/10/2024
#define OFFSET_GLOW_THROUGH_WALLS 0x26C //2 = enabled, 5 = disabled  Script_Highlight_SetVisibilityType //updated 01/10/2024
 
#define OFFSET_TIME_BASE 0x2098 //[DataMap.C_Player].m_currentFramePlayer.timeBase updated 2024/06/26 
#define GLOW_START_TIME 0x02c8 + 0x30 //m_playerFloatLookStartTime=0x02c4 //updated 01/10/2024 DataMap.C_PlayerLocalData
#define OFFSET_HIGHLIGHTSERVERACTIVESTATES 0x298 //updated 11/1/2023

#define OFFSET_GLOW_FIX 0x278        //updated 6/26/2024 
#define GLOW_VISIBLE_TYPE 0x27c      // updated 1/25/2024
#define OFFSET_GLOW_ENABLE_GLOW_CONTEXT OFFSET_GLOW_ENABLE // Script_Highlight_SetCurrentContext updated 01/10/2024
#define OFFSET_GLOW_CONTEXT_ID 0x29c                                            //updated 6/26/2024
#define OFFSET_GLOW_THROUGH_WALLS_GLOW_VISIBLE_TYPE OFFSET_GLOW_THROUGH_WALLS // Script_Highlight_SetVisibilityType 5th mov updated 01/10/2024
#define GLOW_LIFE_TIME 0x3A4+ 0x30 // Script_Highlight_SetLifeTime + 4 updated 01/10/2024
#define GLOW_DISTANCE 0x26c // Script_Highlight_SetFarFadeDist updated 01/10/2024
#define GLOW_TYPE 0x29c // Script_Highlight_GetState + 4 updated 01/10/2024
#define GLOW_COLOR 0x1D0+ 0x30 // Script_CopyHighlightState 15th mov updated 01/10/2024
#define GLOW_FADE 0x388+ 0x30 // ats 3rd result of 3 offsets consecutive or first + 8 updated 01/10/2024
#define HIGHLIGHT_SETTINGS 0xb0d8f70 //[Miscellaneous].HighlightSettings                       //updated 2024/06/26
#define HIGHLIGHT_TYPE_SIZE 0x34 //? updated 01/10/2024
#define OFFSET_CROSSHAIR_LAST OFFSET_VISIBLE_TIME + 0x19a8 //[Miscellaneous].CWeaponX!lastCrosshairTargetTime updated 2024/06/26
//#define OFFSET_CROSSHAIR_START 0x1958 //CPlayer!crosshairTargetStartTime updated 01/9/2024
#define OFFSET_INPUT_SYSTEM 0x18753c0 //[Miscellaneous].InputSystem updated 2024/06/26 

#define OFFSET_SKYDIVE_STATE 0x4734 //[RecvTable.DT_Player].m_skydiveState updated 2024/06/26
#define OFFSET_GRAPPLEACTIVED       0x2d60 //[RecvTable.DT_Player].m_grappleActive updated 2024/06/26
#define OFFSET_GRAPPLE              0x2cd0 //[RecvTable.DT_Player].m_grapple updated 2024/06/26
#define OFFSET_GRAPPLEATTACHED      0x0048 //[RecvTable.DT_GrappleData].m_grappleAttached updated 2024/06/26
#define OFFSET_m_xp					0x3734 //[RecvTable.DT_Player].m_xp updated 2024/06/26
#define OFFSET_GRADE 0x0348 //[RecvTable.DT_BaseEntity].m_grade
