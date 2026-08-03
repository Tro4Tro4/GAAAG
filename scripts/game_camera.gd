class_name GameCamera
extends Camera2D

## Keeps the character on screen in a room wider than the screen.
##
## One camera for the whole game, living next to the characters rather than
## inside a room, for the reason everything else up there lives there: rooms are
## thrown away and this must not be. It is told which character to watch and how
## big the room is, and clamps itself to the second while following the first.
##
## A room the size of the screen — which is every room the game had until now —
## comes out exactly where it always was: the limits leave the camera no room to
## move, so nothing changes and no room has to be told anything.
##
## Note what this does not break. The room already separated the world position
## of a click from its position on the screen, and the interface already lives
## on a CanvasLayer the camera does not move. Both were written that way for
## this day.

## How quickly the camera catches up. Slow enough to read as a camera rather
## than as the room sliding about, fast enough not to lag behind a walk.
const FOLLOW_SPEED: float = 6.0

var _target: PlayerCharacter = null


func _ready() -> void:
	position_smoothing_enabled = true
	position_smoothing_speed = FOLLOW_SPEED


## Watches [param character], or nobody if null.
func follow(character: PlayerCharacter) -> void:
	_target = character

	if _target == null:
		return

	# Snapped rather than eased on a change of character or of room: sliding
	# across a room to catch up with somebody who was already standing there
	# would read as the camera being lost.
	global_position = _clamped(_target.global_position)
	reset_smoothing()


## Fences the camera inside a room [param size] units across.
func frame_room(size: Vector2) -> void:
	limit_left = 0
	limit_top = 0
	limit_right = int(size.x)
	limit_bottom = int(size.y)


func _process(_delta: float) -> void:
	if _target == null or not is_instance_valid(_target):
		return

	# The smoothing is the camera's own; this only says where to head for. The
	# clamping is Godot's, through the limits, and happens after.
	global_position = _target.global_position


func _clamped(point: Vector2) -> Vector2:
	var half: Vector2 = get_viewport_rect().size * 0.5

	return Vector2(
		clampf(point.x, limit_left + half.x, maxf(limit_left + half.x, limit_right - half.x)),
		clampf(point.y, limit_top + half.y, maxf(limit_top + half.y, limit_bottom - half.y))
	)
