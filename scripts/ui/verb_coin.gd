class_name VerbCoin
extends Control

## The little menu of verbs that opens on the object you touched.
##
## One gesture, as in Full Throttle: press on the object, keep the finger down,
## push towards a verb, lift.
##
## Towards, not onto. The verb is chosen by the direction the finger has moved
## from the point the coin opened on, not by what happens to be underneath it.
## At this resolution a verb is a few dozen pixels wide and the finger covers
## it, so asking the player to land on a rectangle asks for precision they
## cannot have and cannot see. A direction they can aim without looking.
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

## How far the finger has to travel before it is aiming at anything. Under
## this it is still a press in place, which means "never mind".
const DEAD_ZONE: float = 12.0

## How far off a verb's direction the finger may be and still pick it. The
## three verbs are 81 degrees apart, so 70 leaves each one a generous target
## and still leaves a cone pointing downwards that picks nothing: dragging
## down and away from the coin is how the player says no.
##
## Kept in degrees rather than as a radian constant: a const is worked out at
## parse time, and whether a built-in call is allowed there is not something
## this project can check from the development machine.
const MAX_AIM_DEGREES: float = 70.0

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

# Where the gesture started: the point the coin opened on. Every direction is
# measured from here.
var _anchor: Vector2 = Vector2.ZERO

# The slice the finger is aiming at, or -1 for none. Lifting runs this one, so
# it is the whole state of the gesture — and it is the one the player can see.
var _highlighted: int = -1


func _ready() -> void:
	visible = false
	_build_buttons()


## Opens the coin for [param hotspot], centred on [param at_position].
func open_for(hotspot: Hotspot, at_position: Vector2) -> void:
	_hotspot = hotspot
	_anchor = at_position
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
		_highlight(_slice_aimed_at(_local_position(event)))
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
			# The highlighted slice, not a fresh look at where the finger is.
			# A fingertip rolls a few pixels as it leaves the glass, so the
			# release lands slightly away from the last movement — and asking
			# again there would sometimes answer "nowhere" right after the
			# player watched a verb light up. What is lit is what runs.
			_choose(_highlighted)

		get_viewport().set_input_as_handled()


func _choose(slice: int) -> void:
	# Closed before the verb goes out, so the coin is gone before anyone reacts
	# to the choice and an action that opens something else does not fight it.
	var hotspot: Hotspot = _hotspot
	close()

	if slice < 0 or hotspot == null:
		return

	verb_chosen.emit(_verbs[slice], hotspot)


## The slice the finger is aiming at from [param point], or -1 for none.
##
## Anywhere outside the dead zone and roughly towards a verb picks it: there is
## no edge to miss and no gap between the slices to fall into. The player
## pushes left, up or right and gets whichever verb lies most nearly that way;
## pushing down instead gets nothing, which is how the gesture is called off.
func _slice_aimed_at(point: Vector2) -> int:
	var aim: Vector2 = point - _anchor
	if aim.length() < DEAD_ZONE:
		return -1

	var chosen: int = -1
	var smallest_angle: float = INF

	for i in _buttons.size():
		# Measured against where the button actually ended up, not against the
		# offset it was asked for: near a screen edge the buttons are pushed
		# back inside, and the direction has to follow them there.
		var towards_button: Vector2 = _buttons[i].get_rect().get_center() - _anchor
		if towards_button.is_zero_approx():
			continue

		var difference: float = absf(rad_to_deg(aim.angle_to(towards_button)))
		if difference < smallest_angle:
			smallest_angle = difference
			chosen = i

	if smallest_angle > MAX_AIM_DEGREES:
		return -1

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
	# silently move every direction away from the buttons they point at.
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
		# The button's own size, not BUTTON_SIZE. A Control refuses to be
		# smaller than the room its content needs, so a Button asked for 34x13
		# comes out taller once the font and the theme margins have had their
		# say. Centring on the requested size would leave every slice sitting
		# slightly below where the code thinks it is.
		var button_size: Vector2 = _buttons[i].size
		var top_left: Vector2 = at_position + BUTTON_OFFSETS[i] - button_size * 0.5
		_buttons[i].position = _kept_on_screen(top_left, button_size)


func _kept_on_screen(top_left: Vector2, button_size: Vector2) -> Vector2:
	var limit: Vector2 = size - button_size - Vector2(SCREEN_MARGIN, SCREEN_MARGIN)
	return Vector2(
		clampf(top_left.x, SCREEN_MARGIN, limit.x),
		clampf(top_left.y, SCREEN_MARGIN, limit.y)
	)
