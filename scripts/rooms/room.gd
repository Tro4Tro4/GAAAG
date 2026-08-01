extends Node2D

## A single game location.
##
## The room is the arbiter of the click. It decides whether the player tapped
## a hotspot or the bare floor, sends the character to the right place, and
## runs the action once the character has arrived. Neither the character nor
## the hotspots know anything about input.

## The line of text at the top of the screen.
##
## Resolved with @onready rather than @export: a node reference written by
## hand into a .tscn is not reliably available yet when the scene root's
## _ready() runs, and this one is needed exactly there.
@onready var caption: Caption = $Caption

## The verb menu. It covers the whole screen while open, so it also acts as
## the thing that swallows a click meant to cancel.
@onready var verb_coin: VerbCoin = $VerbCoin

# How many overlapping shapes a single point query may report. Hotspots are
# not meant to overlap; the allowance is there so that a mistake in a room
# degrades into "the first one wins" instead of silently finding nothing.
const MAX_SHAPES_UNDER_A_POINT: int = 8

# The hotspot the character is walking towards, consumed on arrival. Every
# new click overwrites it, which is what makes changing your mind mid-walk
# cancel the pending action instead of firing it when you get there.
var _pending_hotspot: Hotspot = null

# The verb chosen for _pending_hotspot. Meaningless while that is null.
var _pending_verb: int = Hotspot.Verb.LOOK

# Who this room is currently driving. Held separately from
# GameState.active_character because the room needs the outgoing character
# too, to take its signal connection back off.
var _character: PlayerCharacter = null


func _ready() -> void:
	verb_coin.verb_chosen.connect(_on_verb_chosen)
	GameState.active_character_changed.connect(_take_control_of)

	# Characters register during their own _ready(), which runs before this
	# one, so the first active character was chosen before this room could
	# hear about it. Picking it up by hand is what covers that gap.
	_take_control_of(GameState.active_character)


func _take_control_of(character: PlayerCharacter) -> void:
	# The errand belonged to whoever was walking. Handing control over does
	# not hand over the errand, so it is dropped rather than inherited — and
	# a coin still open belonged to that errand too.
	_pending_hotspot = null
	verb_coin.close()

	if _character != null:
		_character.destination_reached.disconnect(_on_destination_reached)

	_character = character

	if _character != null:
		_character.destination_reached.connect(_on_destination_reached)


func _unhandled_input(event: InputEvent) -> void:
	# _unhandled_input and not _input: the UI (verb-coin, inventory) gets to
	# consume a click first, so pressing a button never also walks the
	# character to the floor underneath it.
	#
	# Only mouse events are handled. On Android the engine turns a tap into
	# one of these on its own — emulate_mouse_from_touch is on by default and
	# the game relies on it — so listening to touch as well would run every
	# action twice. The setting is not written in project.godot: Godot drops
	# any value equal to its default. See CLAUDE.md for why this is deliberate.
	if event is InputEventMouseButton:
		var mouse_event: InputEventMouseButton = event
		if mouse_event.pressed and mouse_event.button_index == MOUSE_BUTTON_LEFT:
			_handle_click(get_global_mouse_position())
			get_viewport().set_input_as_handled()


func _handle_click(click_position: Vector2) -> void:
	if _character == null:
		return

	var hotspot: Hotspot = _hotspot_at(click_position)

	if hotspot != null:
		# Nothing moves yet: the coin opens on the spot that was tapped, and
		# the walk is ordered only once a verb has been chosen. Changing your
		# mind before that costs nothing.
		verb_coin.open_for(hotspot, click_position)
		return

	_pending_hotspot = null
	_walk_to(click_position)


func _on_verb_chosen(verb: int, hotspot: Hotspot) -> void:
	_pending_hotspot = hotspot
	_pending_verb = verb
	_walk_to(hotspot.get_approach_position())


func _walk_to(destination: Vector2) -> void:
	# A navigation map is the server-side merge of every navigation region in
	# this world. Snapping to it means clicking a wall walks to the floor in
	# front of the wall instead of doing nothing — the behaviour every
	# adventure game of the era had.
	var navigation_map: RID = get_world_2d().navigation_map
	_character.walk_to(NavigationServer2D.map_get_closest_point(navigation_map, destination))


## Returns the hotspot under [param point], or null if there is only floor.
func _hotspot_at(point: Vector2) -> Hotspot:
	# The room asks the physics server what sits under the point instead of
	# letting each Area2D react to its own click. That keeps the room the
	# single arbiter, and keeps the hotspot-beats-floor priority written here
	# rather than inherited from the engine's input ordering.
	var query := PhysicsPointQueryParameters2D.new()
	query.position = point
	query.collide_with_areas = true
	query.collide_with_bodies = false

	var space_state := get_world_2d().direct_space_state
	for hit in space_state.intersect_point(query, MAX_SHAPES_UNDER_A_POINT):
		var collider: Object = hit.get("collider")
		if collider is Hotspot:
			return collider

	return null


func _on_destination_reached() -> void:
	if _pending_hotspot == null:
		return

	# Cleared before acting: an action that starts another walk must not find
	# itself still pending when that second walk ends.
	var hotspot: Hotspot = _pending_hotspot
	_pending_hotspot = null

	caption.show_text(hotspot.get_text_for(_pending_verb))
	hotspot.interact(_pending_verb)
