getting started:
cd hybrid-wireless-system
python -m venv .venv
.\ground-control-system\.venv\Scripts\activate
pip install -r .\ground-control-system\requirements.txt

Platformio is required for the pad side microcontroller
Python is required for the ground control laptop

------------------------------------------------------------

Ground Control side is the laptop and user that is controlling the purge, fill, and fire remotely, and receiving load cell data if applicable
It is a system accurate python display with a command line interface to avoid misclicks or accidental actuations of any systems that may be caused by a GUI. 
Ground control sends instructions over radio to the pad side microcontroller where 

Ground control commands:
    ARM - Can only be used in safe mode. Enables the use of fill and fire. Closes and disables the use of purge.
    SAFE - The default state, can only be used in armed mode. Enables the use of purge. Closes and disables the use of fill, and disables the use of fire.
    PURGE - Can only be used in safe mode. Toggles the purge relay that leads to the purge solenoid.
    FILL - Can only be used in armed mode. Toggles the fill relay that leads to the fill solenoid.
    FIRE - Can only be used in armed mode. Toggles the fire relay that leads to the igniter for one second, then deactivates the fire relay AND the fill relay.
    ABORT - Can be used in any mode. Turns off all relays, closing both fill and purge, and returns to safe mode. 
    DUMP - Can only be used in safe mode. Must only be used when bottle is closed but pressure is still in the system. Cycles between fill and fire to dump all idle pressure between the tank and the fill solenoid. This must be done before detaching high pressure equipment from the bottle.
    QUIT - Can only be used in safe mode. Exits the program. This is only available in safe mode to prevent accidental quits during a test firing to ensure a cognizant quit of the program. Asks if you need to dump nitrous to make sure you don't disconnect before relieving the stagnant high pressure 

Press F12 while on the visualizer to toggle topmost mode
You can type "quit-f" at any time to instantly quit the program. Don't do this when connected to any real systems.

(sincerest apologies for my python skills, I am not very knowledgeable about the details about python, I just code until it works and the code looks pretty and acts like c++)

Pad Side is the receiving end of the ground control's instructions.
This is a microcontroller that is receiving instructions such as purge, fill, fire, and custom macros, and then sending back thrust data if a load cell is connected
This is a platformio project since the workflow for platformio allows flexibility in board selection and I prefer using platformio & C++ for microcontrollers that need to be left alone to their own devices (ha)




When moving from a nano to a teensy:
- change the board in platformio.ini
[env:teensy41]
platform = teensy
board = teensy41
default_envs = teensy41

- change serial speed 
- change load cell reading method to non blocking
- pin mappings in main



Wishlist to do:
TCP for commands, UDP for receiving load cell data. Also want call and receive for logging messages, so I can log CMDs as well as if/when they were received
arming servo to flip a physical switch to close the connection to the 12V to fire and fill continuity when the arm command is sent
    ** BUT do not cut the entire 12V loop because the purge still needs to work when on safe, so the switch needs to be perhaps a shared ground for the fill and fire relays
Option to update diagram based on feedback vs local