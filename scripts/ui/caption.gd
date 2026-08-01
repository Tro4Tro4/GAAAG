class_name Caption
extends Label

## The one line of text the game says to the player.
##
## Deliberately minimal: it shows a line and clears it after a while. Real
## dialogue — trees, conditions, several speakers — is a separate system that
## comes later in the plan; this is what stands in for it until then.

## How long a line stays on screen.
@export var seconds_on_screen: float = 2.5

# Identifies the timer that owns the line currently displayed, so that a new
# line replacing an old one does not get cleared by the old one's timer.
var _current_timer: SceneTreeTimer


func _ready() -> void:
	text = ""


## Shows [param new_text], replacing whatever was on screen.
func show_text(new_text: String) -> void:
	text = new_text

	var timer: SceneTreeTimer = get_tree().create_timer(seconds_on_screen)
	_current_timer = timer

	await timer.timeout

	# While this call was waiting, a newer line may have taken over. Clearing
	# the text now would cut that one short.
	if _current_timer == timer:
		text = ""
