extends Node2D

## A single game location.
##
## For now it owns only the click-to-walk loop: clicking anywhere sends the
## character to the closest reachable point of the room's navigation mesh.
## Hotspots and the verb-coin will plug in here, consuming the click before
## the floor ever sees it.

## Assigned in the editor. Once several playable characters exist, the room
## will ask the game state which one is active instead of holding a direct
## reference — that is still an open decision in CLAUDE.md.
@export var player: PlayerCharacter


func _unhandled_input(event: InputEvent) -> void:
	# _unhandled_input and not _input: the UI (verb-coin, inventory) gets to
	# consume a click first, so pressing a button never also walks the
	# character to the floor underneath it.
	if not event is InputEventMouseButton:
		return
	if not event.pressed or event.button_index != MOUSE_BUTTON_LEFT:
		return

	_walk_to_clicked_point(get_global_mouse_position())
	get_viewport().set_input_as_handled()


func _walk_to_clicked_point(click_position: Vector2) -> void:
	# A navigation map is the server-side merge of every navigation region in
	# this world. Snapping the click to it means clicking a wall walks to the
	# floor in front of the wall instead of doing nothing — the behaviour
	# every adventure game of the era had.
	var navigation_map: RID = get_world_2d().navigation_map
	var target: Vector2 = NavigationServer2D.map_get_closest_point(navigation_map, click_position)

	player.walk_to(target)
