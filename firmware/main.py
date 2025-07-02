import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import MatrixScanner
from kmk.keys import KC
from kmk.modules.macros import Macros, Press, Release, Tap
from kmk.extensions.encoder import EncoderHandler
from kmk.extensions.display.oled import DisplayOLED
from kmk.extensions.display.display_text import DisplayText

keyboard = KMKKeyboard()

# Add Macros for key sequences
macros = Macros()
keyboard.modules.append(macros)

# Matrix setup for 3x3 pins
row_pins = (board.D0, board.D1, board.D2)
col_pins = (board.D3, board.D4, board.D5)

#  Add OLED display
oled = DisplayOLED()
display = DisplayText()
oled.display = display
keyboard.extensions.append(oled)

# Add rotary encoder.
encoder = EncoderHandler()
keyboard.extensions.append(encoder)

keyboard.matrix = MatrixScanner(
    rows=row_pins,
    columns=col_pins,
    intervals=5, # Milliseconds
    value_when_pressed=False,
    diode_orientation='COL2ROW'
)

encoder.pins = ((board.D6, board.D7),)

# STATE TRACKING
label_keys = [KC.N1, KC.N2, KC.N3, KC.N4]
current_index = 0
last_input_type = 'Labeling'  # or 'Classification'

def update_oled():
    display.lines = [
        f'Mode: {last_input_type}',
        f'Selected: {label_keys[current_index].name}',
    ]

# Handle rotary encoder turns
def handle_encoder(index, direction):
    global current_index, last_input_type
    
    last_input_type = 'Classification'
    
    if direction == 1:
        current_index = (current_index + 1) % len(label_keys)
    elif direction == -1:
        current_index = (current_index - 1) % len(label_keys)

    keyboard.send(label_keys[current_index])
    update_oled()

encoder.handlers = [handle_encoder]

# Keymap
keyboard.keymap = [
    [ # Row 0
        KC.N1,  # Annotation/Label 1
        KC.N2,  # Annotation/Label 2
        KC.N3,  # Annotation/Label 3
    ],
    [  # Row 1
        KC.N4,  # Annotation/Label 4
        KC.N5,  # Annotation/Label 5
        KC.N6,  # Annotation/Label 6
    ],
    [  # Row 2
        KC.Macro(Press(KC.LCTRL), Tap(KC.Z), Release(KC.LCTRL)),  # Undo
        KC.Macro(Press(KC.LCTRL), Press(KC.LSFT), Tap(KC.Z), Release(KC.LSFT), Release(KC.LCTRL)),  # Redo
        KC.B,  # Annotate
    ],
]

# Track last key for certain action.
@keyboard.on_matrix_key
def handle_key_event(key, pressed, key_number):
    global last_input_type
    if pressed:
        last_input_type = 'Labeling'
        update_oled()

# Initialize OLED at startup.
update_oled()

if __name__ == '__main__':
    keyboard.go()
