# Star Trek style door control w/ MS Teams presence indication
# justin.warwick@gmail.com
# Based on Trinket IO demo

import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn
import touchio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import adafruit_dotstar as dotstar
import time

# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Analog input on D0
analog1in = AnalogIn(board.D0)

# Analog output on D1
aout = AnalogOut(board.D1)

# Digital input with pullup on D2
button = DigitalInOut(board.D2)
button.direction = Direction.INPUT
button.pull = Pull.UP

# Capacitive touch on D3
touch = touchio.TouchIn(board.D3)

# Used if we do HID output, see below
#kbd = Keyboard()

# Establish our palette of colors
RED    = (250,5,3)
GREEN  = (10,252,1)
YELLOW = (200,200,2)
PURPLE = (50,1,190)
GREY   = (6,8,10)
BLUE   = (20,25,215)
COLORS = (GREY,RED,YELLOW,GREEN,BLUE,PURPLE)
#          0    1   2      3     4    5
# And the MS Teams defined Statuses, will correspond to the 
# above indexes into the indication colors.
# Sort of has a "progressively unavailable" quality.
#https://docs.microsoft.com/en-us/microsoftteams/presence-admins
STATUSES = {'AVAILABLE':3,'AWAY':2,'BUSY':1,'OFFLINE':0}

######################### HELPERS FUNCTIONS ####################

# Helper to convert analog input to voltage
def getVoltage(pin):
    return (pin.value * 3.3) / 65536

# Helper to give us a nice color swirl. 
# Just for test/bootup, not for normal operation
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return (0, 0, 0)
    if (pos > 255):
        return (0, 0, 0)
    if (pos < 85):
        return (int(pos * 3), int(255 - (pos*3)), 0)
    elif (pos < 170):
        pos -= 85
        return (int(255 - pos*3), 0, int(pos*3))
    else:
        pos -= 170
        return (0, int(pos*3), int(255 - pos*3))

######################### MAIN LOOP ##############################
sti = 0
i = 0
tick = 0
released = True
while True:
  # spin internal LED around! autoshow is on
  if not touch.value:
    #dot[0] = wheel(i & 255)
    #dot[0] = GREY
    released = True

  # set analog output to 0-3.3V (0-65535 in increments)
  aout.value = i * 256

  # Read analog voltage on D0
  if (i % 255) and time.monotonic() - tick > 10:
      print("D0: %0.2f   i: %d  " % (getVoltage(analog1in),i))
      tick = time.monotonic()

  # use D3 as capacitive touch to signal doorbell/summons
  if touch.value:
      if released:
        #these two lines basically cycle through colors
        #sti = (sti+1) % len(COLORS)
        #dot[0] = COLORS[sti]
        print("#DOOR_SUMMONS")  #("D3 touched!")
      released = False
  led.value = touch.value

  if not button.value:
      print("Button on D2 pressed!")
      # optional! uncomment below & save to have it sent a keypress
      #kbd.press(Keycode.A)
      #kbd.release_all()

  i = (i+1) % 256  # run from 0 to 255 and cycle back to 0
  time.sleep(0.05) # make bigger to slow down