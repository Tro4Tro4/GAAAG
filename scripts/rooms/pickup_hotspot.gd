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

## What has to be true before it can be picked up at all. Empty — the ordinary
## case — means it can always be taken.
##
## Deliberately not the same thing as [member Hotspot.present_if], and the
## difference is the design rule this project keeps coming back to: a slice that
## appeared only when it would work would be telling the player the answer. So a
## thing that cannot be taken *yet* stays in the room, goes on offering Prendi,
## and refuses out loud — the refusal being whatever [member
## Hotspot.hand_text] or a variant on the same conditions has to say. Being
## absent instead would be the wrong half twice over: invisible, and silent
## about why.
##
## Chapter one needs this over and over, because Lino's whole constraint is that
## he may not touch what is under catalogue. The alternative was a script per
## such object, which is what data on the ordinary hotspot exists to avoid.
@export var takeable_if: PackedStringArray = PackedStringArray()

## What Prendi says while [member takeable_if] does not hold.
##
## A field of its own rather than letting the refusal fall through to [member
## Hotspot.hand_text], because hand_text is what is said at the moment the thing
## *is* picked up — the room asks for the line before it calls interact(), so
## both cases would otherwise come out of the same string and one of the two
## would be wrong. Named alongside [member taken_text] on purpose: the three
## states of a pickup are cannot yet, here you are, and already have.
@export_multiline var refused_text: String = ""


## Gone once its item is in somebody's hands. Expressed here rather than as a
## condition in [member Hotspot.present_if] because the flag is derived from the
## item and would otherwise have to be written out a second time, by hand, in
## every room holding a pickup.
func is_present() -> bool:
	return super() and not (vanishes_when_taken and _already_taken())


## True when the conditions for picking this up are met. Asked at the moment of
## the taking rather than worked out when the room was built, like a variant and
## for the same reason: what is in somebody's pocket changes without the room
## being rebuilt.
func can_be_taken() -> bool:
	return Conditions.all_hold(takeable_if, GameState.active_character)


func get_text_for(verb: int) -> String:
	if verb == Verb.TAKE:
		# Already-had beats cannot-have: an object whose conditions have swung
		# back the other way since it was taken is still in somebody's pocket,
		# and saying it cannot be picked up would be a lie about the world.
		if _already_taken() and not taken_text.is_empty():
			return taken_text

		if not can_be_taken() and not refused_text.is_empty():
			return refused_text

	return super(verb)


func interact(verb: int, character: PlayerCharacter) -> void:
	super(verb, character)

	if verb != Verb.TAKE or item == null or character == null:
		return

	if _already_taken() or not can_be_taken():
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
