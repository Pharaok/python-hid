from ctypes import Structure
from enum import IntEnum, auto


USAGE_PAGE = 0x06
class UsagePage(IntEnum):
    GENERIC_DESKTOP = auto()
    SIMULATION_CONTROLS = auto()
    VR_CONTROLS = auto()
    SPORT_CONTROLS = auto()
    GAME_CONTROLS = auto()
    GENERIC_DEVICE_CONTROLS = auto()
    KEYBOARD = auto()
    KEYPAD = KEYBOARD
    LED = auto()
    BUTTON = auto()
    ORDINAL = auto()
    TELEPHONY = auto()
    CONSUMER = auto()
    DIGITIZERS = auto()
    HAPTICS = auto()
    PHYISICAL_INPUT_DEVICE = auto()
    UNICODE = auto()
    EYE_AND_HEAD_TRACKERS = 0x12
    AUXILIARY_DISPLAY = 0x14
    SENSORS = 0x20
    MEDICAL_INSTRUMENT = 0x40
    BRAILLE_DISPLAY = auto()
    LIGHTING_ANDILLUMINATION = 0x59
    MONITOR = 0x80
    MONITOR_ENUMERATED = auto()
    VESA_VIRTUAL_CONTROLS = auto()
    POWER = 0x84
    BATTERY_SYSTEM = auto()
    BARCODE_SCANNER = 0x8C
    SCALES = auto()
    MAGNETIC_STRIPE_READER = auto()
    CAMERA_CONTROL = 0x90
    ARCADE = auto()
    GAMING_DEVICE = auto()
