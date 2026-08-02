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

## Every position here — the anchor, the buttons, the finger — is read
## straight from [member InputEventMouse.position], with no conversion of any
## kind. Do not reach for [method CanvasItem.make_input_local]: an event
## arrives already expressed in the game's 384x216 space, and converting it
## again divides it by the screen's scale factor. On a phone that is a factor
## of five, and the effect is not a wobble but a gesture that always points up
## and to the left, so the first verb wins every time. This cost a debugging
## session; the note is here so it costs no more.

## Emitted when the player picks a verb. The verb is an int rather than
## Hotspot.Verb because an enum in a signal signature is one of the things
## this project cannot verify from the development machine.
signal verb_chosen(verb: int, hotspot: Hotspot)

## The same, for a verb aimed at something in the inventory. A separate signal
## rather than one carrying an Object: the two are answered in completely
## different ways — one starts a walk across the room, the other never leaves
## the interface — and a shared signal would only be un-shared at the far end.
signal item_verb_chosen(verb: int, item: InventoryItem)

const BUTTON_FONT_SIZE: int = 8
const BUTTON_SIZE: Vector2 = Vector2(34, 13)

## Kept away from the screen edge so a button is never half off-screen.
const SCREEN_MARGIN: float = 2.0

## How far the finger has to travel before it is aiming at anything. Under
## this it is still a press in place, which means "never mind".
const DEAD_ZONE: float = 12.0

## How far off a verb's direction the finger may be and still pick it. The
## four verbs are between 52 and 59 degrees apart, so 50 leaves each one a
## target wider than the gap to its neighbour and still leaves a cone pointing
## downwards that picks nothing: dragging down and away is how the player
## says no.
##
## Kept in degrees rather than as a radian constant: a const is worked out at
## parse time, and whether a built-in call is allowed there is not something
## this project can check from the development machine.
const MAX_AIM_DEGREES: float = 50.0

# Where each button sits relative to the touched point: four spread across the
# half-circle above it. Nothing goes below, because that is where the player's
# own finger is and it stays down for the whole gesture — which also leaves the
# downward cone free to mean "never mind".
#
# There is deliberately nothing at straight up: with an even number of slices
# laid out symmetrically, the top is always a boundary. Aiming is done at the
# buttons, which are visible, so it costs nothing.
const BUTTON_OFFSETS: Array = [
	Vector2(-52, -8),
	Vector2(-26, -46),
	Vector2(26, -46),
	Vector2(52, -8),
]

# The words used when the thing under the finger has nothing better to call
# them. A hotspot may rename any slice — a door says "Apri", not "Usa" — but
# only the wording moves: the slice stays where it is and runs the same verb.
var _default_labels: Array[String] = ["Guarda", "Prendi", "Usa", "Parla"]
var _verbs: Array[int] = [
	Hotspot.Verb.LOOK, Hotspot.Verb.TAKE, Hotspot.Verb.USE, Hotspot.Verb.TALK
]

# What the coin was opened on. Exactly one of the two is set at a time.
var _hotspot: Hotspot = null
var _item: InventoryItem = null

var _buttons: Array[Button] = []

# Where the gesture started: the point the coin opened on. Every direction is
# measured from here.
var _anchor: Vector2 = Vector2.ZERO

# The slice the finger is aiming at, or -1 for none. Lifting runs this one, so
# it is the whole state of the gesture — and it is the one the player can see.
var _highlighted: int = -1

# Whether the finger has ever left the dead zone during this gesture. It is
# what tells a plain tap from a drag that ended up pointing nowhere: the first
# runs the subject's usual action, the second means "never mind".
var _has_left_dead_zone: bool = false

# What a plain tap runs, asked of the subject when the coin opens.
var _default_verb: int = Hotspot.Verb.LOOK


func _ready() -> void:
	visible = false
	_build_buttons()


## Opens the coin for [param hotspot], centred on [param at_position].
func open_for(hotspot: Hotspot, at_position: Vector2) -> void:
	_hotspot = hotspot
	_item = null
	_default_verb = hotspot.get_default_verb()

	for i in _buttons.size():
		var label: String = hotspot.get_label_for(_verbs[i])
		_set_label(i, label if not label.is_empty() else _default_labels[i])

	_open_at(at_position)


## Opens the coin for [param item] in the inventory, centred on its slot.
func open_for_item(item: InventoryItem, at_position: Vector2) -> void:
	_item = item
	_hotspot = null

	# Looking is the harmless answer, and the one a stray tap should give.
	_default_verb = Hotspot.Verb.LOOK

	for i in _buttons.size():
		_set_label(i, _default_labels[i])

	_open_at(at_position)


func _set_label(slice: int, text: String) -> void:
	var button: Button = _buttons[slice]
	button.text = text

	# Re-applied straight after the text, and not left to the next layout pass:
	# a longer word raises the button's minimum size, and _place_buttons() reads
	# size to work out where the middle of each slice is. Setting it here forces
	# the recalculation now, so what is measured is what will be drawn.
	button.size = BUTTON_SIZE


func close() -> void:
	visible = false
	_hotspot = null
	_item = null
	_highlight(-1)


func _open_at(at_position: Vector2) -> void:
	_anchor = at_position
	_has_left_dead_zone = false
	_place_buttons(at_position)
	_highlight(-1)
	visible = true


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
		var motion: InputEventMouseMotion = event
		_highlight(_slice_aimed_at(motion.position))
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
			# In a continuous gesture the state is whatever the interface is
			# showing, and the lift confirms it — it is not an opportunity to
			# work it out again. A fingertip also rolls a pixel or two on its
			# way off the glass, so the two answers need not agree.
			_choose(_highlighted)

		get_viewport().set_input_as_handled()


## Answers the finger coming off the glass.
##
## Three outcomes, and the difference between the last two is whether the
## finger ever went anywhere: a tap that stayed put asks for the thing you
## would obviously want, while a drag that ended up pointing at nothing is
## somebody changing their mind.
func _lift() -> void:
	if _highlighted >= 0:
		_choose(_highlighted)
		return

	if not _has_left_dead_zone:
		_run_default()
		return

	close()


func _run_default() -> void:
	var hotspot: Hotspot = _hotspot
	var item: InventoryItem = _item
	var verb: int = _default_verb
	close()

	if hotspot != null:
		verb_chosen.emit(verb, hotspot)
	elif item != null:
		item_verb_chosen.emit(verb, item)


func _choose(slice: int) -> void:
	# Closed before the verb goes out, so the coin is gone before anyone reacts
	# to the choice and an action that opens something else does not fight it.
	var hotspot: Hotspot = _hotspot
	var item: InventoryItem = _item
	close()

	if slice < 0:
		return

	if hotspot != null:
		verb_chosen.emit(_verbs[slice], hotspot)
	elif item != null:
		item_verb_chosen.emit(_verbs[slice], item)


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

	_has_left_dead_zone = true

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


func _build_buttons() -> void:
	for i in _default_labels.size():
		var button := Button.new()
		button.text = _default_labels[i]
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
