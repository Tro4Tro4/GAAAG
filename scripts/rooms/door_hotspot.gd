class_name DoorHotspot
extends Hotspot

## A hotspot that takes whoever used it into another room.
##
## The first hotspot with a script of its own, and the reason the base class
## carries data rather than behaviour: a door needs two extra values and one
## line of code, and a crate needs neither.
##
## Only USE goes anywhere. Looking at a door and talking to it stay ordinary
## lines of text, which is what the base class already does.

## The room this door leads to.
@export_file("*.tscn") var target_room: String = ""

## The name of a Marker2D under EntryPoints in that room — where the character
## comes out. Named rather than given as coordinates so the arrival point is
## dragged into place in the room it belongs to.
@export var target_entry: StringName = &"Default"


func interact(verb: int, character: PlayerCharacter) -> void:
	# The signal fires either way: a door being looked at is still something
	# another system might want to know about.
	super(verb, character)

	if verb != Verb.USE:
		return

	if character == null:
		return

	if target_room.is_empty():
		push_warning("Door %s has no target_room." % name)
		return

	character.move_to_room(target_room, target_entry)
