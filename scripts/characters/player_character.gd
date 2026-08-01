class_name PlayerCharacter
extends CharacterBody2D

## A character that walks to a point when told to.
##
## Pathfinding is delegated to a NavigationAgent2D: the room hands over a
## destination, the agent returns the next corner of the computed path, and
## this script only steers towards that corner. Walking around obstacles is
## therefore a property of the room's navigation mesh, not of this code.

## Emitted once, when the character stops on its destination. Nothing listens
## to it yet; it is what "walk to the hotspot, then act on it" will hang off
## once hotspots exist.
signal destination_reached

## The name shown on the character-switching bar.
@export var display_name: String = ""

## Placeholder until there are sprites: tells one character from another.
@export var body_color: Color = Color(0.92, 0.55, 0.2)

## Pixels per second, expressed at the game's 384x216 base resolution.
@export var walk_speed: float = 55.0

@onready var _body: Polygon2D = $Body

# Resolved with @onready rather than @export: a node reference written by
# hand into a .tscn is not reliably resolved, and the agent is part of this
# same scene anyway, so renaming it means editing this scene regardless.
@onready var _agent: NavigationAgent2D = $NavigationAgent2D

# True while a destination is pending. Without it, destination_reached would
# fire on every frame the character spends standing still.
var _is_walking: bool = false


func _ready() -> void:
	_body.color = body_color
	GameState.register_character(self)


func _exit_tree() -> void:
	# Rooms will be unloaded once there is more than one of them, and a
	# character that left with its room must not stay on the roster.
	GameState.unregister_character(self)


## Sends the character to [param global_target].
func walk_to(global_target: Vector2) -> void:
	# target_position is in global coordinates, not local to this node.
	_agent.target_position = global_target
	_is_walking = true


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
	_is_walking = false
	velocity = Vector2.ZERO
	destination_reached.emit()
