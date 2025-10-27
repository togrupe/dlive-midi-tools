> **_NOTE:_**  The light-grey colored columns are for the Director CSV import feature. All others work based on MIDI.

#### Process?: <br>
* yes - Line is taken into account for dlive-midi-tools data processing <br>
* no - Line is *NOT* part of data processing <br>
With this column you can exclude the particular line from data processing. 

> **_NOTE:_** The column has also effect on DAW & Director CSV Generation process.

#### Name: <br>
Channel-Name, Keep in mind that names longer than 8 characters are going to be trimmed automatically to 8 characters.
<br><br>
"-" ignores the cell. <br><br>
Empty cells are written as blank signs.<br>

Special characters like "äöüéß" are not allowed, otherwise you will get an Error Message.

#### Color: <br>

The following colors are allowed:
* blue
* red 
* light blue 
* purple 
* green 
* yellow 
* black
* white
* "-" - Don´t care. Ignore the cell. <br>

If the given color does not match, the default color black is used instead.

#### Source: (only Director CSV Import) <br>
The following options for dLive are available:
* Unassigned
* MixRack
* Surface
* Surface DX 5/6
* IO 4
* IO 5
* USB
* MixRack DX 1/2
* MixRack DX 3/4
* IO 1
* IO 2
* IO 3
* SigGen

The following options for Avantis are available:
* Unassigned
* Surface
* SLink
* IO 1
* IO 2
* SigGen

#### Socket: (only Director CSV Import) <br>

The Socket number in combination with the `Source` <br>
Allowed values dLive:
* Mixrack: 1-64
* Surface: 1-8
* Surface DX 5/6: 1-32
* IO 4: 1-128
* IO 5: 1-128
* MixRack DX 1/2: 1-32
* MixRack DX 3/4: 1-32
* IO 1: 1-128
* IO 2: 1-128
* IO 3: 1-128

Allowed values Avantis:
* Surface: 1-12
* SLink: 1-128
* IO 1: 1-128
* IO 2: 1-128

#### Gain: (only Director CSV Import) <br>

* "-" - Don´t care. Ignore the cell. <br>
* +5 to +60 - the gain value

#### Pad: (only Director CSV Import) <br>
* yes - to activate PAD <br>
* no - to deactivate PAD. <br>
* "-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.

#### Phantom: (only Director CSV Import) <br>
* yes - to activate Phantom Power (48V) <br>
* no - to deactivate Phantom Power (48V). <br>
* "-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.


#### Mute: <br>
* yes - to mute <br>
* no - to unmute. <br>
* "-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.

#### Fader Level: <br>
Dropdown list with predefined fader level values. (-99 = -inf) <br>
"-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.

#### HPF On (only dLive)
* yes - to activate the Highpass Filter <br>
* no - to deactivate the Highpass Filter <br>
* "-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.

#### HPF Value (only dLive)
20-2000Hz - to set the Highpass Filter value

Empty cells are interpreted as **Don´t care**.

#### Main Mix
yes - Assigns the channel to Main-Mix <br>
no - Removes the assignment from Main Mix <br>
"-" - Don´t care. Ignore the cell. <br>

Empty cells are interpreted as **Don´t care**.

#### Recording
yes - Channel is taken into account for DAW Recording Session <br>
no - Channel will not be part the DAW Recoding session.

Empty cells are interpreted as **no**

#### Record Arm
yes - The Record Button is armed / activated <br>
no - The Record Button is not active

Empty cells are interpreted as **no**

#### DCA1-24 (dLive) / DCA1-16 (Avantis)
By putting an "x" into the relevant cell, the channel will be assigned to the particular DCA Group.

Empty cells are interpreted as not being assigned.

"-" - Don´t care. Ignore the cell. <br>

#### Mute1-8 (Only dLive)
By putting an "x" into the relevant cell, the channel will be assigned to the particular Mute Group.

Empty cells are interpreted as not being assigned.

"-" - Don´t care. Ignore the cell. <br>

[back](../../README.md)