# Pi Pico Programmable Companion Mini Keyboard
# Customized key-sequence input device for when
# you have routinely typed static key sequences.
# The Pi Pico will pretend to be an HID keyboard
# And send in those pre-configured keysequences
# based on triggering event (usually a button press)
# Prereqs:
#   Raspberry Pi Pico, plus nicely wired up buttons on pins: __TODO__
#   the circuitpython build for Pi Pico plus the adafruit lib bundle
#   https://circuitpython.org/libraries
# Refs:
#   https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf
#   https://docs.circuitpython.org/projects/hid/en/latest/
#   https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/gpio
#   https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython?view=all
#   https://learn.adafruit.com/rotary-encoder
import time
import re
import os
import board
import digitalio
import rotaryio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


ROTARY_POSITIONS = 12
BUTTON_COLUMNS   = 2
BUTTON_ROWS      = 4

COLOR_INDICATION = { 'ford':    "blue",
                     'dodge':   "purple",
                     'chevy':   "red",
                     'special': "green"
                   }

print("---             Pi Pieces and Parts             ---")
print("---a Pi Pico Programmable Companion Mini Keyboard---")

onboardLED = digitalio.DigitalInOut(board.LED)
onboardLED.direction = digitalio.Direction.OUTPUT

onboardLED.value = True
keybd.press(Keycode.G)
time.sleep(0.01)
keybd.release(Keycode.G)
keybd.press(Keycode.Q)
time.sleep(0.01)
keybd.release(Keycode.Q)
time.sleep(0.333)
onboardLED.value = False


rotaryEncoder = rotaryio.IncrementalEncoder(board.GP10, board.GP9) #TOD: D? or GP?
keybd = Keyboard(usb_hid.devices)
keybdLayout = KeyboardLayoutUS(keybd)

button = []
# Physical Column 1
button.append([])
button[0].append(digitalio.DigitalInOut(board.GP12))
button[0][0].direction = digitalio.Direction.INPUT
button[0][0].pull      = digitalio.Pull.UP
button[0].append(digitalio.DigitalInOut(board.GP13))
button[0][1].direction = digitalio.Direction.INPUT
button[0][1].pull      = digitalio.Pull.UP
button[0].append(digitalio.DigitalInOut(board.GP14))
button[0][2].direction = digitalio.Direction.INPUT
button[0][2].pull      = digitalio.Pull.UP
button[0].append(digitalio.DigitalInOut(board.GP15))
button[0][3].direction = digitalio.Direction.INPUT
button[0][3].pull      = digitalio.Pull.UP
# Physical Column 2
button.append([])
button[1].append(digitalio.DigitalInOut(board.GP19))
button[1][0].direction = digitalio.Direction.INPUT
button[1][0].pull      = digitalio.Pull.UP
button[1].append(digitalio.DigitalInOut(board.GP18))
button[1][1].direction = digitalio.Direction.INPUT
button[1][1].pull      = digitalio.Pull.UP
button[1].append(digitalio.DigitalInOut(board.GP17))
button[1][2].direction = digitalio.Direction.INPUT
button[1][2].pull      = digitalio.Pull.UP
button[1].append(digitalio.DigitalInOut(board.GP16))
button[1][3].direction = digitalio.Direction.INPUT
button[1][3].pull = digitalio.Pull.UP

indicatorLED = []

def readConfigFile(cfgFilename):
    #Standardized filename format: #pi part numbers.txt
    #broken into sections by whitespace, a color header,
    #the rest is line-by-line button macro assignments.
    realConfigLine = 0
    datafieldsRegEx = re.compile('[\t:\*|│]+')  # just a subset of digram drawing stuff that should appear directly on a data-bearing line.
    buttonMacroMap  = [["" for x in range(BUTTON_COLUMNS)] for y in range(BUTTON_ROWS)]
    blanklineCount = 0

    f = open(cfgFilename)
    for line in f.readlines():
        if re.match("^ *$",line):    # ignore blank lines.
            blanklineCount += 1
        elif re.match("^ *#",line):  # don't process comments, but report them on console.
            onboardLED.value = True
            print("COMMENT: " + line)
        else:
            blanklineCount = 0
            fields = datafieldsRegEx.split(line)
            #DEBUG#
            print("\t" + str(len(fields)) + "l:  " + " ".join(fields) )
            #DEBUG#
            print(re.search("[a-zA-Z0-9]{2,}"," ".join(fields)) )
            # After a split: if it broke up into right number of fields
            # AND there was at least a little "realish-looking" data mixed in,
            # THEN /probably/ it is a valid config line.
            # Overall should avoid weird edge cases of drawing stuff somehow ending up with 4 fields.
            if len(fields) == 4 and re.search("[a-zA-Z0-9_:+#]+", " ".join(fields)):
                print(fields)
                if realConfigLine == BUTTON_ROWS:
                    print("Error: Already reached button row limit, check your config file for valid layout!")
                    #TODO: flash red LED.
                else:
                    realConfigLine = realConfigLine + 1
                    #DEBUG#print("  goodline! ("+str(realConfigLine)+") " + fields[1] + " , " + fields[2])
                    buttonMacroMap[realConfigLine - 1][0] = fields[1]
                    buttonMacroMap[realConfigLine - 1][1] = fields[2]
    f.close()
    print("read in " + str(realConfigLine) + " config lines.")
    return buttonMacroMap


#TODO: dial position validations
controlSet = []
#TODO: also: color-assignment/index position: in file name? in file header? implicit in order?
#TODO: if the files themselves specify color/index, could search working dir
# for button_map*.txt and then just iterate over them and load them all
#   (but if you do this, limit to first n = ROTARY_POSITIONS files)
for filename in os.listdir():
    #Order by alpha
    if re.match("pi[ _]*part[ _]*numbers.txt",filename,re.IGNORECASE):
        print("  Found valid config file: " + filename)
        #TODO: try/catch block
        controlSet.append(readConfigFile(filename))
        makemodel = re.sub("[0-9]+[_-]+button[_-]*index[_-]+","",filename)
        makemodel = re.sub(".txt","",makemodel)
        makemodel = makemodel.lower()
        print("  " + makemodel)
        resplitter = re.compile("[_-]+")
        make,model = resplitter.split(makemodel)
        print("  " + make + "  " + model)
        indicatorLED.append([make,model])
    else:
        print("  Skip non-config file: " + filename)
#controlSet.append(readConfigFile("0_button_index_special_static.txt"))
print(indicatorLED[0][0] + " " + COLOR_INDICATION[indicatorLED[0][0]])

print(controlSet)
print("Keyboard CAPSLOCK status: " + str(keybd.led_on(Keyboard.LED_CAPS_LOCK)))
onboardLED.value = False

cycles = 0
controlSetIndex = 0
buttonPressed = False
last_rotaryPosition = None
while True:  # The Main forever loop
    # TODO: controlSetIndex set by rotaryio dial position
    # and handle looping around (if encoder is not already doing that)
    rotaryPosition = rotaryEncoder.position
    if last_rotaryPosition is None or rotaryPosition != last_rotaryPosition:
        print(rotaryPosition)
        if rotaryPosition < 0:
            controlSetIndex = ROTARY_POSITIONS + (rotaryPosition % ROTARY_POSITIONS)
        else:
            controlSetIndex = rotaryPosition % ROTARY_POSITIONS
    last_rotaryPosition = rotaryPosition

    """
    onboardLED.value = True
    keybd.press(Keycode.G)
    time.sleep(0.01)
    keybd.release(Keycode.G)
    keybd.press(Keycode.Q)
    time.sleep(0.01)
    keybd.release(Keycode.Q)
    time.sleep(0.333)
    onboardLED.value = False
    """

    for x in range(0, BUTTON_COLUMNS - 1):
        for y in range(0, BUTTON_ROWS - 1):
            # Note here, due to "drive high/pull-up" the logic is /inverse/.
            if not button[x][y].value:
                buttonPressed = True
                onboardLED.value = True
                keybdLayout.write(controlSet[controlSetIndex][y][x])

    # Note here, due to "drive high/pull-up" the logic is /inverse/.
    """
    if not button[0][0].value:
        buttonPressed = True
        #TODO: if then else and/or case/switch block to cover all button inputs
        onboardLED.value = True
        # append a '\n' if you need to follow with Enter (a newline).
        #keybdLayout.write(buttonMacroMap[0][0])
        keybdLayout.write(controlSet[controlSetIndex][0][0])
    elif not button[0][1].value:
        buttonPressed = True
        #TODO: if then else and/or case/switch block to cover all button inputs
        onboardLED.value = True
        # append a '\n' if you need to follow with Enter (a newline).
        #keybdLayout.write(buttonMacroMap[0][1])
    """
    #TODO: special FX button handler

    if buttonPressed:
        # Debounce, terminate notification, clean up, etc.
        time.sleep(0.05)
        onboardLED.value = False
        buttonPressed = False

    # TODO: if there is an attached PIr sensor: check for activation state,
    # and send a safe keystroke (maybe a SHIFT press) once or twice to wake-up workstation

    cycles += 1
    if (cycles % 100000) == 0:
        print("10,n cycles more!" + str(onboardLED.value))
        onboardLED.value = not onboardLED.value
        # probably need to handle overflow...

