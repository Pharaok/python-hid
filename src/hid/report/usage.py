from enum import IntEnum, auto


class UsagePages(IntEnum):
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
    PHYSICAL_INPUT_DEVICE = auto()
    UNICODE = auto()
    EYE_AND_HEAD_TRACKERS = 0x12
    AUXILIARY_DISPLAY = 0x14
    SENSORS = 0x20
    MEDICAL_INSTRUMENT = 0x40
    BRAILLE_DISPLAY = auto()
    LIGHTING_AND_ILLUMINATION = 0x59
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


class GenericDesktop(IntEnum):
    POINTER = auto()
    MOUSE = auto()
    JOYSTICK = 0x04
    GAMEPAD = auto()
    KEYBOARD = auto()
    KEYPAD = auto()
    MULTI_AXIS_CONTROLLER = auto()
    TABLET_PC_SYSTEM_CONTROLS = auto()
    WATER_COOLING_DEVICE = auto()
    COMPUTER_CHASSIS_DEVICE = auto()
    WIRELESS_RADIO_CONTROLS = auto()
    PORTABLE_DEVICE_CONTROL = auto()
    SYSTEM_MULTI_AXIS_CONTROLLER = auto()
    SPATIAL_CONTROLLER = auto()
    ASSISTIVE_CONTROL = auto()
    DEVICE_DOCK = auto()
    DOCKABLE_DEVICE = auto()
    CALL_STATE_MANAGEMENT_CONTROL = auto()
    X = auto()
    Y = auto()
    Z = auto()
    RX = auto()
    RY = auto()
    RZ = auto()
    SLIDER = auto()
    DIAL = auto()
    WHEEL = auto()
    HAT_SWITCH = auto()
    COUNTED_BUFFER = auto()
    BYTE_COUNT = auto()
    MOTION_WAKEUP = auto()

class LED(IntEnum):
    NUM_LOCK = auto()
    CAPS_LOCK = auto()
    SCROLL_LOCK = auto()
