# Channels

> **_NOTE:_** The light-grey colored columns are for the Director CSV import feature. All others work based on MIDI.

#### Enabled

* yes — Row is taken into account for dlive-midi-tools data processing
* no — Row is *NOT* part of data processing

With this column you can exclude the particular row from data processing.

> **_NOTE:_** The column also affects DAW & Director CSV generation. If you find the column distracting, you can move it to the right or hide it.

#### Name

Channel name. Keep in mind that names longer than 8 characters are trimmed automatically to 8 characters.

"-" ignores the cell.

Empty cells are written as blank.

Special characters like "äöüéß" are not allowed — you will get an error message if they are used.

#### Color

The following colors are allowed:
* blue
* red 
* light blue 
* purple 
* green 
* yellow 
* black
* white
* "-" — Don't care. Ignore the cell.

If the given color does not match, the validator will report an error and processing will be aborted.

#### Source (only Director CSV Import)

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

#### Socket (only Director CSV Import)

The socket number in combination with the `Source`.

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

#### Gain (only Director CSV Import)

* "-" — Don't care. Ignore the cell.
* +5 to +60 — the gain value

#### Pad (only Director CSV Import)

* yes — activate PAD
* no — deactivate PAD
* "-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.

#### Phantom (only Director CSV Import)

* yes — activate Phantom Power (48V)
* no — deactivate Phantom Power (48V)
* "-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.

#### Mute

* yes — mute
* no — unmute
* "-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.

#### Fader Level

Dropdown list with predefined fader level values. (-99 = -inf)

"-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.

#### HPF On (dLive only)

* yes — activate the Highpass Filter
* no — deactivate the Highpass Filter
* "-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.

#### HPF Value (dLive only)

20–2000 Hz — sets the Highpass Filter frequency.

Empty cells are interpreted as **Don't care**.

#### Main Mix Assignment

* yes — assigns the channel to Main Mix
* no — removes the assignment from Main Mix
* "-" — Don't care. Ignore the cell.

Empty cells are interpreted as **Don't care**.


#### Channel to Group Assignments

> **_NOTE:_** Writing beyond the buses defined in the mixer configuration can lead to internal errors, which can cause strange routings in MGrp1. Use "-" by default for all routings and put an "x" only where routing is actually required.

##### Channel to Mono Group Assignment — Grp1-12 (dLive only)

Put an "x" in the relevant cell to assign the channel to that Mono Group.

Empty cells are interpreted as not assigned.

"-" — Don't care. Ignore the cell.

##### Channel to Stereo Group Assignment — StGrp1-12 (dLive only)

Put an "x" in the relevant cell to assign the channel to that Stereo Group.

Empty cells are interpreted as not assigned.

"-" — Don't care. Ignore the cell.

#### Recording

* yes — channel is included in the DAW recording session
* no — channel is excluded from the DAW recording session

Empty cells are interpreted as **no**.

#### Record Arm

* yes — Record button is armed / activated
* no — Record button is not active

Empty cells are interpreted as **no**.

#### DCA1-24 (dLive) / DCA1-16 (Avantis)

Put an "x" in the relevant cell to assign the channel to that DCA Group.

Empty cells are interpreted as not assigned.

"-" — Don't care. Ignore the cell.

#### Mute1-8 (dLive only)

Put an "x" in the relevant cell to assign the channel to that Mute Group.

Empty cells are interpreted as not assigned.

"-" — Don't care. Ignore the cell.

[back](../../README.md)