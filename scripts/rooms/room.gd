class_name Room
extends Node2D

## A single game location: scenery, hotspots and a navigation mesh.
##
## The room is the arbiter of the click. It decides whether the player tapped a
## hotspot or the bare floor, sends the character to the right place, and runs
## the action once the character has arrived. Neither the character nor the
## hotspots know anything about input.
##
## It knows nothing about the interface either. Rooms are loaded and unloaded
## while the caption, the verb-coin and the switch bar are not, so the room
## reports what it wants said and Game connects that to whatever is listening.
##
## A room is therefore no longer playable on its own: it holds no characters
## and no interface. Main.tscn is the scene to press Play on.

## Emitted when the room has a line for the player.
signal wants_to_say(text: String)

## Emitted when a hotspot was tapped, before anything moves. The position is in
## screen coordinates, because what opens on it is a Control on a CanvasLayer,
## not something living in this room's world.
signal hotspot_activated(hotspot: Hotspot, at_screen_position: Vector2)

## Emitted when the item the player was holding has been used, or given up on.
## The room does not decide what "holding an item" means — it is told, and it
## says when it is over.
signal held_item_released

## Emitted when somebody has walked up to a hotspot with a conversation in it
## and said hello. The room does not run the conversation any more than it runs
## the caption: it reports that one is due and Game sees to it.
signal wants_to_talk(dialogue: Dialogue, character: PlayerCharacter)

## The entry point used when a door names one this room does not have.
const DEFAULT_ENTRY: StringName = &"Default"

## How big this room is, in game units. The camera fences itself inside it.
## The default is exactly one screen, which is what every room was before there
## was a camera — and a room that size leaves the camera nowhere to go, so
## nothing about it changes.
@export var room_size: Vector2 = Vector2(384, 216)

@export_group("Depth")

## The two floor heights between which the room has perspective, and how big
## somebody standing at each of them is.
##
## Not a curve and not a walkbox scale: two numbers and a straight line between
## them, which is all a flat floor seen from one angle needs. Left at 1 and 1 —
## the default — a room has no perspective at all, and nothing scales.
##
## The room owns these because perspective is a property of the room, but it is
## the character who applies them to themselves: a character is not a child of
## the room and never has been, so the room would have nothing to reach for.
@export var depth_top_y: float = 0.0
@export var depth_bottom_y: float = 0.0
@export var depth_top_scale: float = 1.0
@export var depth_bottom_scale: float = 1.0

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

# The item the player picked out of the inventory and has not yet aimed at
# anything. While this is set, a tap on a hotspot means "use it on that" and
# the verb-coin never opens: the sentence is already half written.
var _held_item: InventoryItem = null

# The item travelling with the character towards _pending_hotspot. Separate
# from _held_item because the player may drop the errand mid-walk, and what
# arrives has to be what was set out with.
var _pending_item: InventoryItem = null

# Who this room is currently driving. Handed over by Game rather than read
# from GameState: during a room swap the active character briefly belongs to a
# room that is not on screen, and only Game knows when that has settled.
var _character: PlayerCharacter = null


## Hands [param character] this room's perspective, so it can size itself.
func hand_depth_to(character: PlayerCharacter) -> void:
	if character == null:
		return

	character.set_depth(depth_top_y, depth_bottom_y, depth_top_scale, depth_bottom_scale)


## Hands this room the character the player is controlling.
func set_character(character: PlayerCharacter) -> void:
	# The errand belonged to whoever was walking. Handing control over does
	# not hand over the errand, so it is dropped rather than inherited — and
	# neither does an item held out of somebody else's bag.
	_pending_hotspot = null
	_pending_item = null

	if _character != null and is_instance_valid(_character):
		_character.destination_reached.disconnect(_on_destination_reached)

	_character = character

	if _character != null:
		_character.destination_reached.connect(_on_destination_reached)


## Tells the room which item, if any, the player is carrying in hand.
func set_held_item(item: InventoryItem) -> void:
	_held_item = item


## Sends the character to [param hotspot], to perform [param verb] on arrival.
func begin_action(verb: int, hotspot: Hotspot) -> void:
	if _character == null or hotspot == null:
		return

	_pending_hotspot = hotspot
	_pending_verb = verb
	_walk_to(hotspot.get_approach_position(_character.global_position))


## Where a character arriving through a door named [param entry_name] stands.
##
## The point is a Marker2D under EntryPoints, so it is dragged into place in
## the editor rather than typed in as a pair of numbers — which matters when
## the editor is a phone.
func get_entry_position(entry_name: StringName) -> Vector2:
	var marker: Marker2D = _entry_marker(entry_name)

	if marker == null:
		marker = _entry_marker(DEFAULT_ENTRY)

	if marker != null:
		return marker.global_position

	push_warning("Room %s has no entry point named %s and no %s." % [
		name, entry_name, DEFAULT_ENTRY
	])
	return global_position


func _entry_marker(entry_name: StringName) -> Marker2D:
	var node: Node = get_node_or_null(NodePath("EntryPoints/" + String(entry_name)))
	return node as Marker2D


func _unhandled_input(event: InputEvent) -> void:
	# _unhandled_input and not _input: the UI (verb-coin, switch bar) gets to
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
			# Two coordinate spaces, on purpose: the physics query and the
			# walk destination live in this room's world, the verb-coin lives
			# on the screen. They coincide today and would stop coinciding the
			# first time a room is wider than the screen and scrolls.
			_handle_click(get_global_mouse_position(), mouse_event.position)
			get_viewport().set_input_as_handled()


func _handle_click(world_position: Vector2, screen_position: Vector2) -> void:
	if _character == null:
		return

	var hotspot: Hotspot = _hotspot_at(world_position)

	if _held_item != null:
		# The verb was chosen in the inventory, so the coin stays shut: half
		# the sentence is written and this tap supplies the other half.
		_aim_held_item_at(hotspot)
		return

	if hotspot != null:
		# Nothing moves yet: the coin opens on the spot that was tapped, and
		# the walk is ordered only once a verb has been chosen. Changing your
		# mind before that costs nothing.
		hotspot_activated.emit(hotspot, screen_position)
		return

	_pending_hotspot = null
	_walk_to(world_position)


func _aim_held_item_at(hotspot: Hotspot) -> void:
	_pending_hotspot = hotspot
	_pending_item = null

	if hotspot == null:
		# Bare floor means never mind. The character does not walk there: one
		# tap has to be able to mean "put it away" and nothing else, or calling
		# the sentence off would send somebody across the room first.
		held_item_released.emit()
		return

	_pending_item = _held_item
	_walk_to(hotspot.get_approach_position(_character.global_position))


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

	# Turned towards the thing before anything is said about it. Having walked
	# round to the front of something and then addressing it over your shoulder
	# looks worse than not having walked at all.
	_character.face_towards(hotspot.global_position)

	if _pending_item != null:
		var item: InventoryItem = _pending_item
		_pending_item = null

		wants_to_say.emit(hotspot.get_text_for_item(item))
		hotspot.use_item(item, _character)

		# Released whether or not the hotspot wanted it: a refused item is
		# still an attempt that is over, and leaving it in hand would make the
		# next tap anywhere try the same thing again.
		held_item_released.emit()
		return

	# A conversation replaces the line the hotspot would otherwise have said:
	# what it has to say is inside the conversation, and the reach_text of
	# somebody you can talk to would be a second opening line nobody asked for.
	if _pending_verb == Hotspot.Verb.TALK and hotspot.dialogue != null:
		hotspot.interact(_pending_verb, _character)
		wants_to_talk.emit(hotspot.dialogue, _character)
		return

	wants_to_say.emit(hotspot.get_text_for(_pending_verb))
	hotspot.interact(_pending_verb, _character)
