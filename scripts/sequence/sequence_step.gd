class_name SequenceStep
extends Resource

## One thing that happens during a scripted sequence.
##
## A closed list of kinds, like the verbs are a closed list of words, and for
## the same reason: a sequence that can do anything is a script, and a script
## per object is what this project has spent its whole life avoiding. What is
## here covers the payoff of a puzzle — something is said, something makes a
## noise, somebody moves, the world changes — and anything stranger is still a
## hotspot with a script of its own, which nothing prevents.
##
## Only the fields the kind uses are read; the rest are left at nothing. That is
## clumsier than a resource per kind would be, but sequences are counted in
## dozens where conditions are counted in hundreds, so the verbosity is
## affordable here in a way it was not there.
enum Kind {
	## Says [member text] through the caption and waits for it to be read.
	SAY,
	## Waits [member seconds] with nothing happening.
	WAIT,
	## Sends the character to the point named [member point], and waits until
	## they get there.
	WALK,
	## Turns the character towards the point named [member point].
	FACE,
	## Plays [member sound] once.
	SOUND,
	## Raises the flag named [member name].
	FLAG,
	## Sets the switch named [member name] to [member on].
	SWITCH,
	## Puts [member item] in the character's hands.
	GIVE,
	## Takes [member item] out of them.
	TAKE,
}

@export var kind: Kind = Kind.SAY

## The line to say, as a key. SAY only.
@export_multiline var text: String = ""

## How long to wait. WAIT only — and note that SAY waits by itself, for as long
## as the caption keeps the line up, so a pause after a line is rarely needed.
@export var seconds: float = 1.0

## A named Marker2D under the room's EntryPoints. WALK and FACE.
##
## The same points a door arrives at, on purpose: a room has one set of places
## worth naming, and whether one is used by somebody coming in or by somebody
## being walked about during a scene is not a difference the room cares about.
@export var point: StringName = &""

@export var sound: AudioStream = null

## The flag or switch to set. FLAG and SWITCH.
@export var name: StringName = &""

## Which way to set the switch. SWITCH only.
@export var on: bool = true

@export var item: InventoryItem = null
