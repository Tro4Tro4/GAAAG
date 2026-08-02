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

## Said when a verb leads nowhere. Most objects in an adventure game refuse
## most verbs, and one generic line is how the genre has always covered it.
const REFUSAL: String = "Non mi sembra il caso."

## The name the player sees. Kept apart from the node name so the node can
## stay an English identifier whatever language the game ends up speaking.
@export var display_name: String = ""

@export_multiline var look_text: String = ""
@export_multiline var use_text: String = ""
@export_multiline var talk_text: String = ""

# Where the character stops before acting: an optional child named
# ApproachPoint. Without it the character would walk into the object itself
# — and some hotspots, a door in a wall above all, sit outside the
# navigation mesh entirely, so their own position is not a valid destination.
@onready var _approach_marker: Marker2D = get_node_or_null("ApproachPoint")


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


## Runs [param verb] on this hotspot, on behalf of [param character]. The text
## is the room's business; this is the hook for hotspots that actually do
## something, either by connecting to [signal interacted] or by overriding.
func interact(verb: int, character: PlayerCharacter) -> void:
	interacted.emit(verb, character)


## The point the character should walk to before acting on this hotspot.
func get_approach_position() -> Vector2:
	if _approach_marker != null:
		return _approach_marker.global_position
	return global_position
