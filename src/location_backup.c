#include "location_backup.h"

#include "global.h"

#include "constants/maps.h"

#include "field_system.h"
#include "save_local_field_data.h"

// Rocket Silver: the game opens inside Team Rocket's Mahogany base rather
// than the player's bedroom. (51, 4) is the B1F entrance tile, taken from
// the map's own warp record in zone_event 233_D35R0102.
static const Location sLocation_PlayerRoom = {
    .mapId = MAP_TEAM_ROCKET_HEADQUARTERS_B1F,
    .warpId = 0xFFFFFFFF,
    .x = 51,
    .y = 4,
    .direction = 0x00000001,
};

static const Location sLocation_OutsidePlayerHome = {
    .mapId = MAP_NEW_BARK,
    .warpId = 0xFFFFFFFF,
    .x = 0x000002B7,
    .y = 0x0000018D,
    .direction = 0x00000001,
};

void Location_SetToPlayerRoom(Location *dest) {
    const Location *src = &sLocation_PlayerRoom;
    *dest = *src;
}

void Location_SetToOutsidePlayerHome(Location *dest) {
    const Location *src = &sLocation_OutsidePlayerHome;
    *dest = *src;
}

void Save_SetPositionToPlayerRoom(SaveData *saveData) {
    Location *position = LocalFieldData_GetCurrentPosition(Save_LocalFieldData_Get(saveData));
    Location_SetToPlayerRoom(position);
}
