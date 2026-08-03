class_name Caption
extends Label

## The one line of text the game says to the player.
##
## Deliberately minimal: it shows a line and clears it after a while. It is also
## where conversations are heard — a dialogue does not get a text box of its
## own, it borrows this one and tints it, so that what a person says arrives in
## the same place as what the room says and is told apart by colour.

## How long even the shortest line stays on screen. A floor, not a base: a long
## line does not get this on top of its reading time, it simply takes longer
## than this to read.
@export var minimum_seconds: float = 3.0

## Added per character. A line is on screen for as long as it takes to read,
## which is the only measure that works when the same caption carries a single
## verb and a sentence of a hundred characters.
##
## These two are the knobs a settings screen would turn the day the game has
## one. They are exported and live on the Caption node in Main.tscn, so a slow
## or fast reading speed is two numbers in one place and not a search through
## the code.
@export var seconds_per_character: float = 0.07

## The colour of the narrator: the room's own descriptions, the refusals, the
## word under the finger during a verb-coin gesture. Anything said by somebody
## comes in their own colour instead.
const PLAIN: Color = Color(1, 1, 1)

# Identifies the timer that owns the line currently displayed, so that a new
# line replacing an old one does not get cleared by the old one's timer.
var _current_timer: SceneTreeTimer


func _ready() -> void:
	text = ""


## Shows [param new_text] and leaves it there until somebody says otherwise.
##
## Used while a gesture is in progress: the verb-coin's badges carry pictures,
## so the word for the slice under the finger has to be written here, and it
## must not fade out from under a player who is thinking.
func show_persistent(new_text: String) -> void:
	_current_timer = null
	modulate = PLAIN
	text = tr(new_text)


## Shows [param new_text] as spoken by somebody, in [param color], and leaves it
## there. Persistent because the player is reading their answers underneath it:
## a line that faded out while they were still choosing would take the question
## away with it.
func show_speech(new_text: String, color: Color) -> void:
	show_persistent(new_text)
	modulate = color


func clear() -> void:
	_current_timer = null
	modulate = PLAIN
	text = ""


## Shows [param new_text], replacing whatever was on screen.
func show_text(new_text: String) -> void:
	modulate = PLAIN
	text = tr(new_text)

	await _fade_out()


## Lets whatever is on screen go the way an ordinary line would, keeping its
## colour on the way out. This is how a conversation ends: the last thing said
## stays a moment longer instead of being snatched away with the panel.
func fade() -> void:
	await _fade_out()


func _fade_out() -> void:
	var timer: SceneTreeTimer = get_tree().create_timer(_seconds_for(text))
	_current_timer = timer

	await timer.timeout

	# While this call was waiting, a newer line may have taken over. Clearing
	# the text now would cut that one short.
	if _current_timer == timer:
		modulate = PLAIN
		text = ""


func _seconds_for(line: String) -> float:
	return maxf(minimum_seconds, line.length() * seconds_per_character)
