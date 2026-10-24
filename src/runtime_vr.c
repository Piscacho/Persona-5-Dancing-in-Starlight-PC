/* Devices a PC never has, for Persona 5: Dancing in Starlight:
 *   - PlayStation VR (libSceHmd, libSceVrTracker): no headset is connected;
 *   - PlayStation Camera (libSceCamera): not attached;
 *   - Share Play and system screenshots: accepted and ignored.
 * The game checks for a headset before its VR viewing mode, so every entry reports "absent"
 * instead of pretending a device works. Unknown functions still stop. */
#include "runtime.h"
#include <stdio.h>
#include <string.h>

#define HMD_NOT_CONNECTED ((int32_t)0x81290003)
#define HMD_NOT_INITIALIZED ((int32_t)0x81290002)
#define VRTRACKER_NOT_INITIALIZED ((int32_t)0x81240002)
#define CAMERA_NOT_CONNECTED ((int32_t)0x802E0010)
#define CAMERA_NOT_OPEN ((int32_t)0x802E0004)
#define HMD_STATUS_NOT_DETECTED 2

static ABI int32_t ok(void) { return 0; }

/* ---- PlayStation VR headset ---- */
static int hmd_initialized;
static ABI int32_t hmd_initialize(const void *param) {
    (void)param;
    if (!hmd_initialized) puts("Runtime: PlayStation VR not connected (HMD reports no device)");
    hmd_initialized=1;
    return 0;
}
static ABI int32_t hmd_terminate(void) { hmd_initialized=0; return 0; }
/* OrbisHmdDeviceInformation starts with status, user id, then device data: only the status
 * and user are written, the game's buffer size is unknown beyond that. */
static ABI int32_t hmd_device_information(void *info) {
    if (!info) return (int32_t)0x81290001;
    int32_t head[2]={HMD_STATUS_NOT_DETECTED,-1};
    memcpy(info,head,sizeof(head));
    return 0;
}
static ABI int32_t hmd_device_information_by_handle(int32_t handle,void *info) {
    (void)handle; (void)info; return HMD_NOT_CONNECTED;
}
static ABI int32_t hmd_open(int32_t user,int32_t type,int32_t index,const void *param) {
    (void)user; (void)type; (void)index; (void)param;
    return hmd_initialized ? HMD_NOT_CONNECTED : HMD_NOT_INITIALIZED;
}
static ABI int32_t hmd_handle_call(int32_t handle) { (void)handle; return HMD_NOT_CONNECTED; }
static ABI int32_t hmd_query_onion_size(void) { return 0x100000; }
static ABI int32_t hmd_query_garlic_size(void) { return 0x100000; }
static ABI int32_t hmd_query_align(void) { return 0x100; }

/* ---- VR tracker (needs a headset and camera) ---- */
static ABI int32_t vrtracker_unavailable(void) { return VRTRACKER_NOT_INITIALIZED; }

/* ---- PlayStation Camera ---- */
static ABI int32_t camera_is_attached(int32_t index) { (void)index; return 0; }
static ABI int32_t camera_open(int32_t user,int32_t type,int32_t index,const void *param) {
    (void)user; (void)type; (void)index; (void)param; return CAMERA_NOT_CONNECTED;
}
static ABI int32_t camera_not_open(void) { return CAMERA_NOT_OPEN; }

static const RuntimeExport exports[]={
    {"sceHmdInitialize",hmd_initialize}, {"sceHmdInitialize315",hmd_initialize},
    {"sceHmdTerminate",hmd_terminate},
    {"sceHmdGetDeviceInformation",hmd_device_information},
    {"sceHmdGetDeviceInformationByHandle",hmd_device_information_by_handle},
    {"sceHmdOpen",hmd_open}, {"sceHmdClose",hmd_handle_call},
    {"sceHmdGetFieldOfView",hmd_handle_call}, {"sceHmdGet2DEyeOffset",hmd_handle_call},
    {"sceHmdReprojectionInitialize",ok}, {"sceHmdReprojectionFinalize",ok},
    {"sceHmdReprojectionQueryOnionBuffSize",hmd_query_onion_size},
    {"sceHmdReprojectionQueryOnionBuffAlign",hmd_query_align},
    {"sceHmdReprojectionQueryGarlicBuffSize",hmd_query_garlic_size},
    {"sceHmdReprojectionQueryGarlicBuffAlign",hmd_query_align},
    {"sceHmdReprojectionSetDisplayBuffers",hmd_handle_call},
    {"sceHmdReprojectionUnsetDisplayBuffers",ok},
    {"sceHmdReprojectionStartWithOverlay",hmd_handle_call},
    {"sceHmdReprojectionStop",ok}, {"sceHmdReprojectionSetUserEventStart",ok},
    {"sceVrTrackerInit",vrtracker_unavailable}, {"sceVrTrackerTerm",ok},
    {"sceVrTrackerQueryMemory",vrtracker_unavailable},
    {"sceVrTrackerRegisterDevice",vrtracker_unavailable}, {"sceVrTrackerUnregisterDevice",ok},
    {"sceVrTrackerGpuSubmit",vrtracker_unavailable}, {"sceVrTrackerGpuWaitAndCpuProcess",vrtracker_unavailable},
    {"sceVrTrackerGetResult",vrtracker_unavailable}, {"sceVrTrackerGetTime",vrtracker_unavailable},
    {"sceVrTrackerRecalibrate",vrtracker_unavailable},
    {"sceVrTrackerUpdateMotionSensorData",vrtracker_unavailable},
    {"sceCameraIsAttached",camera_is_attached}, {"sceCameraOpen",camera_open},
    {"sceCameraClose",camera_not_open}, {"sceCameraStart",camera_not_open}, {"sceCameraStop",camera_not_open},
    {"sceCameraSetConfig",camera_not_open}, {"sceCameraSetVideoSync",camera_not_open},
    {"sceCameraGetFrameData",camera_not_open},
    {"sceSharePlayInitialize",ok}, {"sceSharePlaySetProhibition",ok},
    {"sceScreenShotEnable",ok}, {"sceScreenShotDisable",ok}, {"sceScreenShotSetOverlayImageWithOrigin",ok},
    {"sceSystemServiceShowDisplaySafeAreaSettings",ok},
};
uintptr_t runtime_vr_resolve(const char *name) { return RUNTIME_LOOKUP(exports,name); }
