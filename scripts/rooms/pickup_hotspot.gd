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
##
## This was the first hotspot to have to remember anything, and it did its own
## remembering by hand. Now that the base class can be told what has to be true
## for a hotspot to be there and what it says once things have changed, most of
## that is gone: what is left is the part no general mechanism could supply,
## which is that the flag is derived from the item instead of written out.

## What the player gets. The flag that records the taking is derived from this
## item's id, so there is nothing else to fill in and nothing to keep in step.
@export var item: InventoryItem = null

## Whether the hotspot itself disappears once the item is gone.
@export var vanishes_when_taken: bool = true

## What TAKE says afterwards, for a hotspot that stays. Falls back to the
## ordinary [member Hotspot.hand_text] when empty.
##
## Shorthand for a [HotspotVariant] conditioned on "taken:<id>", kept because it
## is two fields instead of a block of sub-resource and because the flag comes
## out of the item on its own. A variant written by hand on the same condition
## wins over it, being the more deliberate of the two.
@export_multiline var taken_text: String = ""


## Gone once its item is in somebody's hands. Expressed here rather than as a
## condition in [member Hotspot.present_if] because the flag is derived from the
## item and would otherwise have to be written out a second time, by hand, in
## every room holding a pickup.
func is_present() -> bool:
	return super() and not (vanishes_when_taken and _already_taken())


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
	#
	# Raising it is also what makes the hotspot go away, if it is the kind that
	# does: GameState announces the flag, every hotspot in the room works out
	# again whether it is there, and this one finds that it is not. Hence no
	# queue_free() here any more — and none of the awkwardness that freeing
	# would cause the day a taken thing has to be put back.
	GameState.raise_flag(_taken_flag())
	character.take(item)


func _taken_flag() -> StringName:
	if item == null:
		return &""

	return StringName("taken:" + String(item.id))


func _already_taken() -> bool:
	return item != null and GameState.is_raised(_taken_flag())
