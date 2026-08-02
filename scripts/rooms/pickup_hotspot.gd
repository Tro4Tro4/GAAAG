class_name PickupHotspot
extends Hotspot

## A hotspot that hands over an item the first time it is taken.
##
## Covers both shapes the genre needs. A key lying on the floor *is* the item,
## so it goes away once taken ([member vanishes_when_taken]); a crate you take
## something out of stays where it is and only changes what it has to say.
##
## Taking is recorded as a flag in GameState rather than in the hotspot,
## because the hotspot does not survive leaving the room. Without that, walking
## out and back in would refill the crate and the same item could be had twice.

## What the player gets. The flag that records the taking is derived from this
## item's id, so there is nothing else to fill in and nothing to keep in step.
@export var item: InventoryItem = null

## Whether the hotspot itself disappears once the item is gone.
@export var vanishes_when_taken: bool = true

## What TAKE says afterwards, for a hotspot that stays. Falls back to the
## ordinary [member Hotspot.take_text] when empty.
@export_multiline var taken_text: String = ""


func _ready() -> void:
	if vanishes_when_taken and _already_taken():
		queue_free()


func get_text_for(verb: int) -> String:
	if verb == Verb.TAKE and _already_taken() and not taken_text.is_empty():
		return taken_text

	return super(verb)


func interact(verb: int, character: PlayerCharacter) -> void:
	super(verb, character)

	if verb != Verb.TAKE or item == null or character == null:
		return

	if _already_taken():
		return

	# Raised before the item is handed over: if anything later reacts to the
	# flag, it should find a world in which the taking has already happened.
	GameState.raise_flag(_taken_flag())
	character.take(item)

	if vanishes_when_taken:
		queue_free()


func _taken_flag() -> StringName:
	if item == null:
		return &""

	return StringName("taken:" + String(item.id))


func _already_taken() -> bool:
	return item != null and GameState.is_raised(_taken_flag())
