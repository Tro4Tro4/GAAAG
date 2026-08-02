class_name VerbCoin
extends Control

## The little menu of verbs that opens on the object you touched.
##
## One gesture, as in Full Throttle: press on the object, keep the finger down,
## slide onto a verb, lift. Lifting anywhere else cancels.
##
## The whole gesture is read in _input(), by hand, instead of letting the
## buttons report their own presses. That is not a preference, it is forced:
## the press that opens the coin is consumed by the room while the coin is
## still hidden, so Godot never records the coin as the control being dragged
## — and the release that ends the gesture would be routed somewhere else
## entirely. Reading the raw events sidesteps the question. The buttons are
## left as pure visuals and never see an event.
##
## The node covers the whole screen on purpose. While open it swallows every
## mouse event, so nothing reaches the room underneath and a stray lift
## cancels instead of ordering a walk.

## Emitted when the player picks a verb. The verb is an int rather than
## Hotspot.Verb because an enum in a signal signature is one of the things
## this project cannot verify from the development machine.
signal verb_chosen(verb: int, hotspot: Hotspot)

const BUTTON_FONT_SIZE: int = 8
const BUTTON_SIZE: Vector2 = Vector2(34, 13)

## Kept away from the screen edge so a button is never half off-screen.
const SCREEN_MARGIN: float = 2.0

## How far outside a verb still counts as being on it. A verb is 34x13 pixels
## at this resolution and a fingertip is nowhere near that precise, so the area
## that answers is deliberately larger than the area that is drawn.
const TOUCH_MARGIN: float = 6.0

# Where each button sits relative to the touched point: two at the sides and
# one above. Below would put the button under the player's own finger — which
# matters more now than it did, because the finger stays down the whole time.
const BUTTON_OFFSETS: Array = [
	Vector2(-38, -6),
	Vector2(0, -26),
	Vector2(38, -6),
]

# The three slices, in the order they are laid out.
var _labels: Array[String] = ["Guarda", "Usa", "Parla"]
var _verbs: Array[int] = [Hotspot.Verb.LOOK, Hotspot.Verb.USE, Hotspot.Verb.TALK]

var _hotspot: Hotspot = null
var _buttons: Array[Button] = []

# The slice the finger is currently over, or -1 for none. Lifting the finger
# turns this into the verb that runs, so it is the whole state of the gesture.
var _highlighted: int = -1


func _ready() -> void:
	visible = false
	_build_buttons()


## Opens the coin for [param hotspot], centred on [param at_position].
func open_for(hotspot: Hotspot, at_position: Vector2) -> void:
	_hotspot = hotspot
	_place_buttons(at_position)
	_highlight(-1)
	visible = true


func close() -> void:
	visible = false
	_hotspot = null
	_highlight(-1)


func _input(event: InputEvent) -> void:
	# _input and not _unhandled_input: while the coin is open it outranks
	# everything, the switch bar included. While it is closed it costs one
	# comparison per event and lets the rest of the game work as before.
	#
	# The press that opens the coin never gets here, and that is what makes
	# this safe: _input runs before the room's _unhandled_input, so at that
	# moment the coin is still invisible and returns on the line below.
	if not visible:
		return

	if event is InputEventMouseMotion:
		_highlight(_slice_at(_local_position(event)))
		get_viewport().set_input_as_handled()
		return

	if event is InputEventMouseButton:
		var button_event: InputEventMouseButton = event
		if button_event.button_index != MOUSE_BUTTON_LEFT:
			return

		if button_event.pressed:
			# A second press with no release in between cannot happen with one
			# finger. Should the engine produce one anyway, reading it as
			# "never mind" is the safe way out.
			close()
		else:
			_choose(_slice_at(_local_position(event)))

		get_viewport().set_input_as_handled()


func _choose(slice: int) -> void:
	# Closed before the verb goes out, so the coin is gone before anyone reacts
	# to the choice and an action that opens something else does not fight it.
	var hotspot: Hotspot = _hotspot
	close()

	if slice < 0 or hotspot == null:
		return

	verb_chosen.emit(_verbs[slice], hotspot)


## The slice under [param point], or -1 when the finger is not on one.
func _slice_at(point: Vector2) -> int:
	var chosen: int = -1
	var best_distance: float = INF

	for i in _buttons.size():
		var area: Rect2 = Rect2(_buttons[i].position, BUTTON_SIZE).grow(TOUCH_MARGIN)
		if not area.has_point(point):
			continue

		# Where two enlarged areas overlap, the nearer centre wins. Without
		# this the answer would depend on the order the buttons were built in,
		# which is not something the player can see or predict.
		var distance: float = point.distance_squared_to(
			_buttons[i].position + BUTTON_SIZE * 0.5
		)
		if distance < best_distance:
			best_distance = distance
			chosen = i

	return chosen


func _highlight(slice: int) -> void:
	if slice == _highlighted:
		return

	_highlighted = slice

	for i in _buttons.size():
		# toggle_mode plus button_pressed is what draws a Button in its pressed
		# style with nobody having pressed it. The highlight then comes from the
		# theme, instead of needing a second set of art to maintain.
		_buttons[i].button_pressed = i == _highlighted


func _local_position(event: InputEvent) -> Vector2:
	# The coin sits at the origin of a CanvasLayer, so today this changes
	# nothing. It is written out anyway so that moving the node does not
	# silently move every hit area away from what is drawn.
	var local_event := make_input_local(event) as InputEventMouse
	return local_event.position


func _build_buttons() -> void:
	for i in _labels.size():
		var button := Button.new()
		button.text = _labels[i]
		button.size = BUTTON_SIZE
		button.custom_minimum_size = BUTTON_SIZE
		button.add_theme_font_size_override("font_size", BUTTON_FONT_SIZE)

		# Nothing here is driven by the keyboard, and a focus ring left behind
		# after the coin closes would be a ghost of a menu that is gone.
		button.focus_mode = Control.FOCUS_NONE

		# Pure visuals: the gesture is read in _input(), so a button must never
		# intercept an event or decide anything on its own.
		button.mouse_filter = Control.MOUSE_FILTER_IGNORE
		button.toggle_mode = true

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
