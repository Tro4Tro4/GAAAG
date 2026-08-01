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

## Temporary. Prints what happens at every step of a click, so a failure can
## be located instead of guessed. Turn off once click-to-walk is confirmed.
@export var debug_clicks: bool = true


func _ready() -> void:
	if player == null:
		player = get_node_or_null("Player")
		push_warning("The 'player' export was empty; fell back to the Player child node.")

	if not debug_clicks:
		return

	print("[Room] player = ", player)

	var map: RID = get_world_2d().navigation_map
	print("[Room] map cell size = ", NavigationServer2D.map_get_cell_size(map))

	# The navigation map is only synchronised at the end of a physics frame,
	# so counting regions any earlier always reports zero.
	await get_tree().physics_frame
	print("[Room] regions in map = ", NavigationServer2D.map_get_regions(map).size())
	print("[Room] sample snap of (192, 200) -> ", NavigationServer2D.map_get_closest_point(map, Vector2(192, 200)))


func _unhandled_input(event: InputEvent) -> void:
	# _unhandled_input and not _input: the UI (verb-coin, inventory) gets to
	# consume a click first, so pressing a button never also walks the
	# character to the floor underneath it.
	#
	# Mouse and touch are handled separately. On Android a tap may arrive as
	# a touch event, as an emulated mouse click, or as both, depending on the
	# project's input settings — covering both is the only reliable option.
	if event is InputEventMouseButton:
		if debug_clicks:
			print("[Room] mouse button: pressed=", event.pressed, " index=", event.button_index)
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			_walk_to_clicked_point(get_global_mouse_position())
			get_viewport().set_input_as_handled()

	elif event is InputEventScreenTouch:
		if debug_clicks:
			print("[Room] screen touch: pressed=", event.pressed, " at ", event.position)
		if event.pressed:
			# make_input_local converts viewport coordinates into this node's
			# own space, which is what the navigation map expects.
			var local_event: InputEventScreenTouch = make_input_local(event)
			_walk_to_clicked_point(local_event.position)
			get_viewport().set_input_as_handled()


func _walk_to_clicked_point(click_position: Vector2) -> void:
	# A navigation map is the server-side merge of every navigation region in
	# this world. Snapping the click to it means clicking a wall walks to the
	# floor in front of the wall instead of doing nothing — the behaviour
	# every adventure game of the era had.
	var navigation_map: RID = get_world_2d().navigation_map
	var target: Vector2 = NavigationServer2D.map_get_closest_point(navigation_map, click_position)

	if debug_clicks:
		print("[Room] click at ", click_position, " -> snapped to ", target)

	player.walk_to(target)
