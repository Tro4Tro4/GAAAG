class_name VerbCoin
extends Control

## The little menu of verbs that opens on the object you tapped.
##
## Two taps: one on the object opens the coin, one on a verb runs it. Tapping
## anywhere else closes it. The alternative — hold, slide onto a verb, release,
## as in Full Throttle — is faster once learned but has to be written by hand,
## and on a phone the finger covers exactly what it is choosing.
##
## The node covers the whole screen on purpose. While open it swallows every
## click, so nothing reaches the room underneath and a stray tap cancels
## instead of ordering a walk.

## Emitted when the player picks a verb. The verb is an int rather than
## Hotspot.Verb because an enum in a signal signature is one of the things
## this project cannot verify from the development machine.
signal verb_chosen(verb: int, hotspot: Hotspot)

const BUTTON_FONT_SIZE: int = 8
const BUTTON_SIZE: Vector2 = Vector2(34, 13)

## Kept away from the screen edge so a button is never half off-screen.
const SCREEN_MARGIN: float = 2.0

# Where each button sits relative to the tapped point: two at the sides and
# one above. Below would put the button under the player's own finger.
const BUTTON_OFFSETS: Array = [
	Vector2(-38, -6),
	Vector2(0, -26),
	Vector2(38, -6),
]

var _hotspot: Hotspot = null
var _buttons: Array[Button] = []


func _ready() -> void:
	visible = false
	_build_buttons()


## Opens the coin for [param hotspot], centred on [param at_position].
func open_for(hotspot: Hotspot, at_position: Vector2) -> void:
	_hotspot = hotspot
	_place_buttons(at_position)
	visible = true


func close() -> void:
	visible = false
	_hotspot = null


func _gui_input(event: InputEvent) -> void:
	# Only reached when the tap missed every button: the buttons are children
	# and are offered the event first. Tapping beside the coin means "never
	# mind", which is how the coin has always been dismissed.
	if event is InputEventMouseButton:
		var mouse_event: InputEventMouseButton = event
		if mouse_event.pressed:
			close()
			accept_event()


func _build_buttons() -> void:
	var labels: Array[String] = ["Guarda", "Usa", "Parla"]
	var verbs: Array[int] = [Hotspot.Verb.LOOK, Hotspot.Verb.USE, Hotspot.Verb.TALK]

	for i in labels.size():
		var button := Button.new()
		button.text = labels[i]
		button.size = BUTTON_SIZE
		button.custom_minimum_size = BUTTON_SIZE
		button.add_theme_font_size_override("font_size", BUTTON_FONT_SIZE)

		# Nothing here is driven by the keyboard, and a focus ring left behind
		# after the coin closes would be a ghost of a menu that is gone.
		button.focus_mode = Control.FOCUS_NONE

		button.pressed.connect(_on_verb_pressed.bind(verbs[i]))
		add_child(button)
		_buttons.append(button)


func _place_buttons(at_position: Vector2) -> void:
	for i in _buttons.size():
		var top_left: Vector2 = at_position + BUTTON_OFFSETS[i] - BUTTON_SIZE * 0.5
		_buttons[i].position = _kept_on_screen(top_left)


func _kept_on_screen(top_left: Vector2) -> Vector2:
	var limit: Vector2 = size - BUTTON_SIZE - Vector2(SCREEN_MARGIN, SCREEN_MARGIN)
	return Vector2(
		clampf(top_left.x, SCREEN_MARGIN, limit.x),
		clampf(top_left.y, SCREEN_MARGIN, limit.y)
	)


func _on_verb_pressed(verb: int) -> void:
	# Closing first means the coin is gone before anyone reacts to the choice,
	# so an action that opens something else does not fight with it.
	var hotspot: Hotspot = _hotspot
	close()

	if hotspot != null:
		verb_chosen.emit(verb, hotspot)
