class_name Hotspot
extends Area2D

## A clickable thing in a room: a door, a crate, a panel.
##
## A hotspot carries data, not behaviour. Most of them only need a name, a few
## lines of description and a place to stand — no script of their own. The ones
## that actually do something connect to [signal interacted] or extend this
## class.
##
## An Area2D is used purely as a shape the room can query. The hotspot does
## not listen for its own clicks: the room decides what a click means, so the
## priority between hotspot and floor lives in one place.

## What the player can do to a hotspot. Three verbs, as in The Curse of Monkey
## Island: "take" lives inside USE, and walking is not a verb — you click the
## floor for that.
enum Verb { LOOK, USE, TALK }

## Emitted after the character has reached this hotspot and acted on it. The
## verb is an int rather than Verb for the same reason as in VerbCoin.
##
## The character is carried along because with several playable characters
## "who did it" is half the answer: a door has to move the person who opened
## it, and picking something up will have to put it in somebody's hands.
signal interacted(verb: int, character: PlayerCharacter)

## Emitted after an inventory item has been used on this hotspot, whether or
## not it was the item this hotspot was waiting for.
signal item_used(item: InventoryItem, character: PlayerCharacter)

## Said when a verb leads nowhere. Most objects in an adventure game refuse
## most verbs, and one generic line is how the genre has always covered it.
const REFUSAL: String = "Non mi sembra il caso."

## Said when the wrong item is used on this hotspot — which, given an inventory
## and a roomful of objects, is nearly every pairing the player will attempt.
const ITEM_REFUSAL: String = "Non c'entra niente con questo."

## The name the player sees. Kept apart from the node name so the node can
## stay an English identifier whatever language the game ends up speaking.
@export var display_name: String = ""

@export_multiline var look_text: String = ""
@export_multiline var use_text: String = ""
@export_multiline var talk_text: String = ""

@export_group("Reaction to an item")

## The one item this hotspot does something about. One and not a list, for the
## same reason a hotspot has no script by default: a single expected item
## covers the ordinary lock-and-key case as data, and anything cleverer is a
## hotspot with a script of its own.
@export var accepted_item: InventoryItem = null

@export_multiline var accepted_text: String = ""

## Whether the item is used up. A key that opens a door is usually gone
## afterwards; a screwdriver is not.
@export var consumes_accepted_item: bool = true

## Raised when the accepted item is used, so the effect survives the room being
## thrown away and rebuilt. Optional: leave it empty for a hotspot whose
## reaction is only a line of text.
@export var accepted_flag: StringName = &""


## The line to show for [param verb], or the generic refusal if this hotspot
## has nothing to say about it.
func get_text_for(verb: int) -> String:
	var text: String = ""

	match verb:
		Verb.LOOK:
			text = look_text
		Verb.USE:
			text = use_text
		Verb.TALK:
			text = talk_text

	return text if not text.is_empty() else REFUSAL


## The line to show when [param item] is used on this hotspot.
func get_text_for_item(item: InventoryItem) -> String:
	if not accepts(item):
		return ITEM_REFUSAL

	return accepted_text if not accepted_text.is_empty() else REFUSAL


## True when [param item] is the one thing this hotspot is waiting for.
func accepts(item: InventoryItem) -> bool:
	return item != null and item == accepted_item


## Runs [param verb] on this hotspot, on behalf of [param character]. The text
## is the room's business; this is the hook for hotspots that actually do
## something, either by connecting to [signal interacted] or by overriding.
func interact(verb: int, character: PlayerCharacter) -> void:
	interacted.emit(verb, character)


## Uses [param item] on this hotspot, on behalf of [param character].
func use_item(item: InventoryItem, character: PlayerCharacter) -> void:
	if accepts(item):
		GameState.raise_flag(accepted_flag)

		if consumes_accepted_item and character != null:
			character.give_up(item)

	item_used.emit(item, character)


## The point the character should walk to before acting on this hotspot.
func get_approach_position() -> Vector2:
	# Looked up on the spot rather than held in an @onready field. It costs a
	# node lookup per interaction, which is nothing at the rate a player clicks,
	# and it buys something worth more: this class has no _ready(), so a
	# subclass can write its own without having to remember to call super()
	# to keep a field it cannot see initialised.
	var marker: Node = get_node_or_null("ApproachPoint")

	# Without one the character would walk into the object itself — and some
	# hotspots, a door in a wall above all, sit outside the navigation mesh
	# entirely, so their own position is not a valid destination.
	if marker is Marker2D:
		return (marker as Marker2D).global_position

	return global_position
