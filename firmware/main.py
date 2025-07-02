import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.keys import KC
from kmk.modules.macros import Macros, Press, Release, Tap
from kmk.extensions.encoder import EncoderHandler
from kmk.extensions.display.oled import DisplayOLED
from kmk.extensions.display.display_text import DisplayText

keyboard = KMKKeyboard()

# Macros support
macros = Macros()
keyboard.modules.append(macros)

# Encoder support
encoder_ext = EncoderHandler()
keyboard.extensions.append(encoder_ext)

# OLED display setup
oled = DisplayOLED()
display = DisplayText()
oled.display = display
keyboard.extensions.append(oled)

# GPIO for key switches (replace with actual pinout)
PINS = [board.D0, board.D1, board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8]

keyboard.matrix = KeysScanner(
    pins=PINS,
    value_when_pressed=False,
)

# Encoder pins
ENCODER_A = board.D9
ENCODER_B = board.D10
encoder_ext.pins = ((ENCODER_A, ENCODER_B),)

# === TRACK STATE ===
label_keys = [KC.N1, KC.N2, KC.N3, KC.N4]
current_index = 0
last_input_type = 'Labeling'  # Default

def update_oled():
    display.lines = [
        f'Mode: {last_input_type}',
        f'Selected: {label_keys[current_index].name}',
    ]

# Rotary encoder behavior
def handle_encoder(index, direction):
    global current_index, last_input_type
    last_input_type = 'Classification'

    if direction == 1:
        current_index = (current_index + 1) % len(label_keys)
    elif direction == -1:
        current_index = (current_index - 1) % len(label_keys)

    keyboard.send(label_keys[current_index])
    update_oled()

encoder_ext.handlers = [handle_encoder]

# Keymap includes mode-tracking
def mode_wrapped(keycode):
    def wrapper(*args, **kwargs):
        global last_input_type
        last_input_type = 'Labeling'
        update_oled()
        return keycode(*args, **kwargs)
    return wrapper

# Actual keymap (wrap label buttons to update mode)
keyboard.keymap = [[
    mode_wrapped(lambda: KC.N1),  # Button 1
    mode_wrapped(lambda: KC.N2),  # Button 2
    mode_wrapped(lambda: KC.N3),  # Button 3
    mode_wrapped(lambda: KC.N4),  # Button 4
    KC.N5,  # Button 5
    KC.N6,  # Button 6
    KC.Macro(Press(KC.LCTRL), Tap(KC.Z), Release(KC.LCTRL)),  # Undo
    KC.Macro(Press(KC.LCTRL), Press(KC.LSFT), Tap(KC.Z), Release(KC.LSFT), Release(KC.LCTRL)),  # Redo
    KC.B,  # Annotate (B)
]]

# Initialize OLED on boot
update_oled()

if __name__ == '__main__':
    keyboard.go()
