class_name Fade
extends ColorRect

## The black that a room change happens behind.
##
## Not decoration: without it the swap is a single frame in which one room is
## replaced by another, and the eye reads that as a glitch rather than as going
## somewhere. Half a beat of black is what turns it into a door.
##
## It is also the only thing in the interface that is deliberately in the way.
## A Control with the default mouse filter eats the click during Godot's own
## GUI pass, which runs before the room's _unhandled_input, so while this is up
## nothing underneath can be tapped — and it is hidden the rest of the time so
## that it is never in the way when it is not wanted.

## How long each half of a transition takes. Two of these end to end, so the
## whole thing is under half a second: long enough to read as a change, short
## enough that walking through a door does not become a wait.
const SECONDS: float = 0.22

var _tween: Tween = null


func _ready() -> void:
	visible = false
	color = Color(color.r, color.g, color.b, 0.0)


func is_fading() -> bool:
	return _tween != null and _tween.is_valid()


## Stands in the way without being seen: still transparent, but visible, which
## is what makes it eat clicks. This is how a scripted scene stops the player
## half-cancelling it — the same trick the panels use, with nothing drawn.
func block() -> void:
	visible = true


func unblock() -> void:
	if not is_fading():
		visible = false


## Goes to black, calls [param action], and comes back.
##
## The action runs in a tween callback, which is idle time — the same reason
## the room swap used to be deferred. A door is used at the end of a walk, and
## a walk ends inside a physics step, where handing the physics server a new set
## of collision shapes is not allowed.
func cover_then(action: Callable) -> void:
	if is_fading():
		# Already mid-transition. Starting a second fade over the first would
		# throw away whichever action had not run yet, so this one is done now
		# and the fade already on screen covers it.
		action.call()
		return

	visible = true

	_tween = create_tween()
	_tween.tween_property(self, "color:a", 1.0, SECONDS)
	_tween.tween_callback(action)
	_tween.tween_property(self, "color:a", 0.0, SECONDS)
	_tween.tween_callback(_finish)


func _finish() -> void:
	visible = false
	_tween = null
