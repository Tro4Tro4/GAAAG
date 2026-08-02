class_name PlayerCharacter
extends CharacterBody2D

## A character that walks to a point when told to.
##
## Pathfinding is delegated to a NavigationAgent2D: the room hands over a
## destination, the agent returns the next corner of the computed path, and
## this script only steers towards that corner. Walking around obstacles is
## therefore a property of the room's navigation mesh, not of this code.
##
## Characters are children of Game, not of a room, and live for the whole
## session. A character whose room is not on screen is hidden and stops
## processing, but never leaves the tree — which is why its position needs no
## saving anywhere, and why it stays on the switch bar while it is elsewhere.

## Emitted once, when the character stops on its destination. The room listens
## to it to run the verb the player chose.
signal destination_reached

## Emitted when this character has gone through a door. Game listens, and puts
## the new room on screen if this is the character the player is controlling.
signal room_changed(character: PlayerCharacter)

## The name shown on the character-switching bar.
@export var display_name: String = ""

## Placeholder until there are sprites: tells one character from another.
@export var body_color: Color = Color(0.92, 0.55, 0.2)

## Pixels per second, expressed at the game's 384x216 base resolution.
@export var walk_speed: float = 55.0

## The scene file of the room this character is standing in: set here for the
## room they start in, and changed by walking through a door. It is the only
## record of where anybody is — there is no separate table of positions,
## because the character node itself is never unloaded.
@export_file("*.tscn") var current_room: String = ""

@onready var _body: Polygon2D = $Body

# Resolved with @onready rather than @export: a node reference written by
# hand into a .tscn is not reliably resolved, and the agent is part of this
# same scene anyway, so renaming it means editing this scene regardless.
@onready var _agent: NavigationAgent2D = $NavigationAgent2D

# True while a destination is pending. Without it, destination_reached would
# fire on every frame the character spends standing still.
var _is_walking: bool = false

# Where this character should be put down when its room next comes on screen.
# Empty for anyone who did not just come through a door.
var _pending_entry: StringName = &""


func _ready() -> void:
	_body.color = body_color
	GameState.register_character(self)


func _exit_tree() -> void:
	# A safety net rather than a mechanism: characters are meant to outlive
	# every room. Should one ever be freed anyway, it must not stay on the
	# roster and leave a dead button on the switch bar.
	GameState.unregister_character(self)


## Sends the character to [param global_target].
func walk_to(global_target: Vector2) -> void:
	# target_position is in global coordinates, not local to this node.
	_agent.target_position = global_target
	_is_walking = true


## Moves the character to another room, to arrive at [param entry_name].
func move_to_room(room_path: String, entry_name: StringName) -> void:
	_cancel_walk()
	current_room = room_path
	_pending_entry = entry_name
	room_changed.emit(self)


## Returns the entry point owed to this character, and forgets it. Empty when
## the character did not arrive through a door.
func consume_pending_entry() -> StringName:
	var entry: StringName = _pending_entry
	_pending_entry = &""
	return entry


## Puts the character down at [param new_position], cancelling any walk.
func place_at(new_position: Vector2) -> void:
	_cancel_walk()
	global_position = new_position


## Shows or hides the character according to whether its room is on screen.
##
## Hiding alone would not be enough: visibility does not stop _physics_process,
## so a hidden character would go on walking across a navigation mesh that is
## no longer loaded. PROCESS_MODE_DISABLED stops the node and its children.
func set_present(is_present: bool) -> void:
	visible = is_present
	process_mode = Node.PROCESS_MODE_INHERIT if is_present else Node.PROCESS_MODE_DISABLED

	if not is_present:
		_cancel_walk()


func _physics_process(_delta: float) -> void:
	if not _is_walking:
		return

	if _agent.is_navigation_finished():
		_stop_walking()
		return

	# The agent returns the next corner of the path, never the final
	# destination directly: steering corner by corner is what makes the
	# character go around an obstacle instead of into it.
	var next_corner: Vector2 = _agent.get_next_path_position()
	velocity = global_position.direction_to(next_corner) * walk_speed

	# move_and_slide() applies velocity using the physics frame time on its
	# own, which is why delta is not multiplied in here.
	move_and_slide()


func _stop_walking() -> void:
	_cancel_walk()
	destination_reached.emit()


func _cancel_walk() -> void:
	# Silent, unlike _stop_walking(): destination_reached would run the room's
	# pending action, and a walk is cancelled precisely when that room is
	# about to stop being the one on screen.
	_is_walking = false
	velocity = Vector2.ZERO
