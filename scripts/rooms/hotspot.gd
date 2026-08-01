class_name Hotspot
extends Area2D

## A clickable thing in a room: a door, a crate, a panel.
##
## A hotspot carries data, not behaviour. Most of them only need a name, a
## description and a place to stand — no script of their own. The ones that
## actually do something connect to [signal interacted] or extend this class.
##
## An Area2D is used purely as a shape the room can query. The hotspot does
## not listen for its own clicks: the room decides what a click means, so the
## priority between hotspot and floor lives in one place.

## Emitted after the character has reached this hotspot and acted on it.
signal interacted

## The name the player sees. Kept apart from the node name so the node can
## stay an English identifier whatever language the game ends up speaking.
@export var display_name: String = ""

## What the default "look at" action says about this hotspot.
@export_multiline var look_text: String = ""

# Where the character stops before acting: an optional child named
# ApproachPoint. Without it the character would walk into the object itself
# — and some hotspots, a door in a wall above all, sit outside the
# navigation mesh entirely, so their own position is not a valid destination.
@onready var _approach_marker: Marker2D = get_node_or_null("ApproachPoint")


## Runs the default action. The verb-coin will eventually pick between
## several of these; for now looking is the only thing anyone can do.
func interact() -> void:
	interacted.emit()


## The point the character should walk to before acting on this hotspot.
func get_approach_position() -> Vector2:
	if _approach_marker != null:
		return _approach_marker.global_position
	return global_position
