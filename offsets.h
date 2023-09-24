#define VERSION STEAM

#if VERSION == STEAM

#define OFFSET_ENTITYLIST 0x1e23418

#define OFFSET_LOCAL_ENT 0x21d3758

#define OFFSET_INPUTSYSTEM 0x1774cc0

#define OFFSET_GLOBALVAR 0x16f6d20

#define OFFSET_NAME_LIST 0xc266a60

#define OFFSET_LEVEL_NAME 0x16f71e0

#define OFFSET_STUDIOHDR 0x1020

#define OFFSET_CAMERAPOS 0x1e90

#define OFFSET_MATRIX 0x11a350

#define OFFSET_RENDER 0x74210a8

#define OFFSET_ZOOM_FOV 0x15f0 + 0xb8

#define OFFSET_ZOOMING 0x1b91

#define OFFSET_YAW 0x21fc - 0x8

#define OFFSET_AIMPUNCH 0x23f8

#define OFFSET_THIRDPERSON 0x01db1f70 + 0x6c

#define OFFSET_TIMESCALE 0x01768ad0

#define OFFSET_HEALTH 0x036c

#define OFFSET_ARMORTYPE 0x45c4

#define OFFSET_LIFE_STATE 0x06c8

#define OFFSET_BLEED_OUT_STATE 0x26a0

#define OFFSET_VIEWANGLES 0x24f4 - 0x14

#define OFFSET_BONES 0x0dd0 + 0x48

#define OFFSET_TEAM 0x037c

#define OFFSET_SHIELD 0x01a0

#define OFFSET_MAXSHIELD 0x01a4

#define OFFSET_NAME 0x04b9

#define OFFSET_SIGN_NAME 0x04b0

#define OFFSET_ABS_VELOCITY 0x0170

#define OFFSET_THIRDPERSON_SV 0x3650

#define OFFSET_OBSERVER_MODE 0x3454

#define OFFSET_OBSERVING_TARGET 0x3460

#define OFFSET_WEAPON 0x1954

#define OFFSET_AMMO 0x1574

#define OFFSET_ITEM_ID 0x1578

#define OFFSET_IN_JUMP 0x07422950

#define OFFSET_IN_DUCK 0x07422a48

#define OFFSET_FLAGS 0x00c8

#define OFFSET_IN_FORWARD 0x07422798

#define OFFSET_m_grappleAttached 0x0048

#define OFFSET_m_grappleActivateTime 0x0054

#define OFFSET_TIME_BASE 0x2048

#define OFFSET_TRAVERSAL_STARTTIME 0x2ac0

#define OFFSET_TRAVERSAL_PROGRESS 0x2abc

#define OFFSET_WALL_RUN_START_TIME 0x3524

#define OFFSET_WALL_RUN_CLEAR_TIME 0x3528

#define OFFSET_SKYDIVE_STATE 0x4620


// OFFSETS that need to be changed manually
#define OFFSET_ORIGIN  0x017c
#define OFFSET_ITEM_GLOW  0x0294
#define OFFSET_VISIBLE_TIME  0x19b0
#define OFFSET_m_grapple  0x2ca8
#define OFFSET_CURRENT_FRAME OFFSET_GLOBALVAR + 0x0008
#define OFFSET_BREATH_ANGLES  OFFSET_VIEWANGLES - 0x10
#define OFFSET_BULLET_SPEED  OFFSET_VISIBLE_TIME + 0x04d4 //0x1f6c //0x1aa0 + 0x04cc // WeaponSettingsMeta.base + WeaponSettings.projectile_launch_speed
#define OFFSET_BULLET_SCALE  OFFSET_VISIBLE_TIME + 0x04dc //0x1f74 //0x1aa0 + 0x04d4 // WeaponSettingsMeta.base + WeaponSettings.projectile_gravity_scale
#define OFFSET_GLOW_T1  0x292 //16256 = enabled, 0 = disabled
#define OFFSET_GLOW_T2  0x30c //1193322764 = enabled, 0 = disabled
#define OFFSET_GLOW_ENABLE  0x02cc //0x3c8 //7 = enabled, 2 = disabled [RecvTable.DT_HighlightSettings] -> m_highlightServerContextID + 0x8
#define OFFSET_GLOW_THROUGH_WALLS  0x02d4 //2 = enabled, 5 = disabled [RecvTable.DT_HighlightSettings] -> m_highlightServerContextID + 0x10
#define GLOW_TYPE  0x2c4 + 0x30
#define GLOW_COLOR_R  0x200
#define GLOW_COLOR_G  GLOW_COLOR_R + 0x04
#define GLOW_COLOR_B  GLOW_COLOR_G + 0x04

#endif
