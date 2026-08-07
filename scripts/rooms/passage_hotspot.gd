class_name PassageHotspot
extends Hotspot

## A way to send an object somewhere a character cannot follow it.
##
## Two of these in two rooms, sharing a [member cache_id], are the two ends of
## the same slot: what one character posts through, another takes out on the
## far side. It is [DoorHotspot] applied to objects instead of to people, and
## it is the only way anything moves between two inventories.
##
## That is deliberate. With one bag per character, a general "hand it over"
## would make carrying the wrong thing a walk rather than a problem, and the
## separate inventories would stop earning their keep. Here every exchange is
## somewhere in particular, so the question is never "how do I give him this"
## but "where can this get through, and what fits".
##
## A passage with only one end is a hiding place: leave something, come back
## for it later. That falls out for free and needs no extra code.

## Said when there is nothing waiting and nothing was written for the occasion.
const NOTHING_THERE: String = "GENERIC_PASSAGE_EMPTY"

## Said when something goes in and nothing was written for the occasion.
const POSTED: String = "GENERIC_PASSAGE_POSTED"

## The name this passage shares with its twin. Two hotspots with the same
## cache_id are two ends of one slot; a name used only once is a hiding place.
@export var cache_id: StringName = &""

## What fits, if the passage is fussy — a gap under a door takes flat objects
## and nothing else. Left empty, anything goes through.
##
## A list and not one item, which it was until the office had two different
## things to send down the same tube. One item was also a trap of its own: with
## no list at all the tube happily swallowed the box of papers Lino is carrying
## and is told to hold on to, handed it to Cesare, and there was no way back.
@export var fits_only: Array[InventoryItem] = []

@export_multiline var posted_text: String = ""

## What LOOK says while something is waiting to be collected. Without it the
## other character has no way of knowing anything arrived.
@export_multiline var waiting_text: String = ""


func get_text_for(verb: int) -> String:
	var waiting: Array[InventoryItem] = GameState.cache_contents(cache_id)

	if verb == Verb.LOOK and not waiting.is_empty() and not waiting_text.is_empty():
		return waiting_text

	if verb == Verb.TAKE:
		if waiting.is_empty():
			return hand_text if not hand_text.is_empty() else NOTHING_THERE

		# Built from what is actually in there rather than written by hand:
		# a passage cannot know in advance what will come through it.
		#
		# Translated here and not by the caption, because this is the one line
		# in the game that is assembled instead of looked up: what comes out is
		# already a sentence, and tr() on a sentence hands it straight back.
		var names: Array[String] = []
		for item in waiting:
			names.append(tr(item.display_name))
		return tr("GENERIC_PASSAGE_TAKE") % ", ".join(names)

	return super(verb)


## Anything fits unless the passage was told to be fussy.
func accepts(item: InventoryItem) -> bool:
	if item == null:
		return false

	return fits_only.is_empty() or fits_only.has(item)


func get_text_for_item(item: InventoryItem) -> String:
	if not accepts(item):
		return ITEM_REFUSAL

	return posted_text if not posted_text.is_empty() else POSTED


func interact(verb: int, character: PlayerCharacter) -> void:
	super(verb, character)

	if verb != Verb.TAKE or character == null:
		return

	for item in GameState.empty_cache(cache_id):
		character.take(item)


func use_item(item: InventoryItem, character: PlayerCharacter) -> void:
	# Written out instead of leaning on the base class's consumes_accepted_item:
	# an item that went into the passage but stayed in the bag would exist
	# twice, and that is too easy to cause by setting one exported flag wrong.
	if accepts(item) and character != null:
		character.give_up(item)
		GameState.put_in_cache(cache_id, item)
		GameState.raise_flag(accepted_flag)

	item_used.emit(item, character)
