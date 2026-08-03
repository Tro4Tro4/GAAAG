class_name StateVisual
extends Node2D

## A piece of scenery that is only there while its conditions hold.
##
## The counterpart of [member Hotspot.present_if], for the things a room draws
## but nobody clicks: the light an open door spills on the floor, the shut leaf
## of that same door, a lamp that comes on. Grouping several polygons under one
## of these is the point — a state is usually more than one shape.
##
## Why not a hotspot with no verbs: a hotspot answers clicks, and a wedge of
## light lying across the floor in front of a door would sit exactly where the
## player taps to walk there. Scenery that reacts to the world should not also
## compete for the tap.
##
## It listens to the same three announcements a hotspot does, and works itself
## out from scratch each time. Nothing is deferred here because there is no
## collision shape to hand to the physics server — only a visibility flag, which
## can be set at any moment.

## All of these must hold for this to be drawn. See [Conditions] for the
## grammar. Empty means always, which would make it an ordinary Node2D.
@export var visible_if: PackedStringArray = PackedStringArray()


func _ready() -> void:
	GameState.flag_raised.connect(_refresh.unbind(1))
	GameState.switch_changed.connect(_refresh.unbind(2))
	GameState.active_character_changed.connect(_refresh.unbind(1))

	_refresh()


func _refresh() -> void:
	visible = Conditions.all_hold(visible_if, GameState.active_character)
