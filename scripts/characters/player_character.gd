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

## Pixels per second, expressed at the game's 384x216 base resolution.
@export var walk_speed: float = 55.0

## Assigned in the editor rather than looked up by node path: a path breaks
## silently the moment the node is renamed or moved.
@export var agent: NavigationAgent2D

# True while a destination is pending. Without it, destination_reached would
# fire on every frame the character spends standing still.
var _is_walking: bool = false


## Sends the character to [param global_target].
func walk_to(global_target: Vector2) -> void:
	# target_position is in global coordinates, not local to this node.
	agent.target_position = global_target
	_is_walking = true


func _physics_process(_delta: float) -> void:
	if not _is_walking:
		return

	if agent.is_navigation_finished():
		_stop_walking()
		return

	# The agent returns the next corner of the path, never the final
	# destination directly: steering corner by corner is what makes the
	# character go around an obstacle instead of into it.
	var next_corner: Vector2 = agent.get_next_path_position()
	velocity = global_position.direction_to(next_corner) * walk_speed

	# move_and_slide() applies velocity using the physics frame time on its
	# own, which is why delta is not multiplied in here.
	move_and_slide()


func _stop_walking() -> void:
	_is_walking = false
	velocity = Vector2.ZERO
	destination_reached.emit()
