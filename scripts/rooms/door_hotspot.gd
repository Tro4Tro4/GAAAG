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
const OPENING: String = "GENERIC_DOOR_OPEN"
const CLOSING: String = "GENERIC_DOOR_CLOSE"

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

@export_group("Not yet")

## What has to be true before this door lets anybody through. Empty — the
## ordinary case — means it always does.
##
## The twin of [member PickupHotspot.takeable_if], and for the same reason: a
## way through that is not open to you *yet* stays in the room, goes on offering
## Vai, and refuses out loud. Making it disappear, or dropping the verb, would
## tell the player the answer — the rule this project keeps coming back to.
##
## Deliberately not [member state_id]. That is a door standing open or shut,
## which the player can see and can change by hand; this is whether they are
## allowed through at all, which they cannot see and cannot change without
## having done something else first. A checkpoint is not a door that is shut.
@export var locked_if: PackedStringArray = PackedStringArray()

## What Vai says while [member locked_if] does not hold. This is where the
## reason goes, and there should always be one: a refusal with no reason reads
## as a bug in a genre where most things refuse most of the time.
@export_multiline var locked_text: String = ""


## True when whoever is asking may go through. Worked out at the moment of
## asking, not when the room was built: what is in a pocket, or who is asking,
## changes without the room being rebuilt.
func is_passable() -> bool:
	return Conditions.all_hold(locked_if, GameState.active_character)


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

	# Checked before falling through, so the refusal takes the place of the line
	# about going somewhere — which would otherwise be said by somebody who is
	# not going anywhere.
	if verb == Verb.GO and not is_passable() and not locked_text.is_empty():
		return locked_text

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

	# The refusal has already been said by then — the room asks for the line
	# before calling this — so there is nothing to say here, only somewhere not
	# to go. Note that the door is not opened either: a checkpoint that swings
	# open as you are turned away would be a strange thing to leave behind.
	if not is_passable():
		return

	if target_room.is_empty():
		push_warning("Door %s has no target_room." % name)
		return

	# Going through a shut door opens it on the way. The alternative — refusing
	# until the player opens it first — would turn every doorway into two taps
	# to buy a state nobody asked to manage.
	GameState.set_switch(state_id, true)
	character.move_to_room(target_room, target_entry)
