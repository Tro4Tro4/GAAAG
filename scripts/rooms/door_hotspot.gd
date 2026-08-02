class_name DoorHotspot
extends Hotspot

## A hotspot that takes whoever used it into another room.
##
## The first hotspot with a script of its own, and the reason the base class
## carries data rather than behaviour: a door needs a few extra values and a
## handful of lines, and a crate needs neither.
##
## A door uses two of the four slices. The one for doing something to a thing
## holds OPEN or CLOSE, whichever the door is not at the moment; the one for
## where a thing leads holds GO. Nothing goes in the other two: a door is not
## picked up and has nobody in it to talk to, and a slice with nothing to say
## is better left undrawn than shown greyed.

## Said while opening or shutting, when nothing was written for the occasion.
const OPENING: String = "Apri la porta."
const CLOSING: String = "Chiudi la porta."

## The room this door leads to.
@export_file("*.tscn") var target_room: String = ""

## The name of a Marker2D under EntryPoints in that room — where the character
## comes out. Named rather than given as coordinates so the arrival point is
## dragged into place in the room it belongs to.
@export var target_entry: StringName = &"Default"

@export_group("Open and shut")

## The name under which this door remembers being open. Left empty, the door
## has no state at all: it is simply a way through, and the slice that would
## say "Apri" goes back to saying whatever the base class says.
##
## It is a two-way switch and not a flag, because a door can go back to being
## shut and a flag by design cannot. Both ends of the same doorway should share
## one name, so opening it from one side opens it from the other.
@export var state_id: StringName = &""

@export_multiline var opening_text: String = ""
@export_multiline var closing_text: String = ""


## True when the door stands open. A door with no state is never in the way.
func is_open() -> bool:
	return state_id.is_empty() or GameState.is_on(state_id)


## The door offers whichever of the two it is not: a shut door can be opened,
## an open one shut. It is the one thing about a hotspot that may change from
## one opening of the coin to the next, and it is safe because it only ever
## reflects something the player can already see.
func get_verb_for(slot: int) -> int:
	if slot == Slot.ACT and not state_id.is_empty():
		return Verb.CLOSE if is_open() else Verb.OPEN

	return super(slot)


func get_text_for(verb: int) -> String:
	if verb == Verb.OPEN:
		return opening_text if not opening_text.is_empty() else OPENING

	if verb == Verb.CLOSE:
		return closing_text if not closing_text.is_empty() else CLOSING

	return super(verb)


func interact(verb: int, character: PlayerCharacter) -> void:
	# The signal fires either way: a door being looked at is still something
	# another system might want to know about.
	super(verb, character)

	if verb == Verb.OPEN or verb == Verb.CLOSE:
		GameState.set_switch(state_id, verb == Verb.OPEN)
		return

	if verb != Verb.GO:
		return

	if character == null:
		return

	if target_room.is_empty():
		push_warning("Door %s has no target_room." % name)
		return

	# Going through a shut door opens it on the way. The alternative — refusing
	# until the player opens it first — would turn every doorway into two taps
	# to buy a state nobody asked to manage.
	GameState.set_switch(state_id, true)
	character.move_to_room(target_room, target_entry)
