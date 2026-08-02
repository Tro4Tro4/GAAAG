class_name VerbCoin
extends Control

## The little menu of verbs that opens on the object you touched.
##
## One gesture, as in Full Throttle: press on the object, keep the finger down,
## push towards a verb, lift.
##
## Towards, not onto. The verb is chosen by the direction the finger has moved
## from the point the coin opened on, not by what happens to be underneath it.
## At this resolution a badge is a couple of dozen pixels across and the finger
## covers it, so asking the player to land on one asks for precision they
## cannot have and cannot see. A direction they can aim without looking.
##
## The four slices are round badges carrying an icon, not words. An icon is
## read at a glance and needs no translating, but it can only ever mean the
## generic verb — so the object's own word for it ("Apri" rather than "Usa")
## goes to the caption at the top of the screen, which is the one place the
## finger never covers and where a long word still fits.
##
## The whole gesture is read in _input(), by hand, instead of letting the
## buttons report their own presses. That is not a preference, it is forced:
## the press that opens the coin is consumed by the room while the coin is
## still hidden, so Godot never records the coin as the control being dragged
## — and the release that ends the gesture would be routed somewhere else
## entirely. Reading the raw events sidesteps the question. The badges are
## left as pure visuals and never see an event.
##
## The node covers the whole screen on purpose. While open it swallows every
## mouse event, so nothing reaches the room underneath and a stray lift
## cancels instead of ordering a walk.

## Every position here — the anchor, the badges, the finger — is read
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

## The word for the slice the finger is on, or "" when it is on none. Now that
## the badges carry pictures, this is the only place the verb is spelled out.
signal aim_changed(label: String)

## The icons, in slice order. Vector files rather than pixel art: a badge is
## about twenty pixels across in game units but several times that on a real
## screen, and a drawing of an eye made of twenty pixels is not an eye.
const ICON_PATHS: Array = [
	"res://assets/ui/verb_look.svg",
	"res://assets/ui/verb_take.svg",
	"res://assets/ui/verb_use.svg",
	"res://assets/ui/verb_talk.svg",
]

const BADGE_SIZE: Vector2 = Vector2(24, 24)

## Only used if the icons fail to load, in which case the coin falls back to
## the words it used before there were pictures.
const FALLBACK_SIZE: Vector2 = Vector2(44, 16)
const FALLBACK_FONT_SIZE: int = 8

## Kept away from the screen edge so a badge is never half off-screen.
const SCREEN_MARGIN: float = 2.0

## How far the finger has to travel before it is aiming at anything. Under
## this it is still a press in place, which runs the object's usual action.
const DEAD_ZONE: float = 12.0

## How far off a verb's direction the finger may be and still pick it. The
## four verbs are around fifty degrees apart, so 50 leaves each one a target
## wider than the gap to its neighbour and still leaves a cone pointing
## downwards that picks nothing: dragging down and away is how the player
## says no.
##
## Kept in degrees rather than as a radian constant: a const is worked out at
## parse time, and whether a built-in call is allowed there is not something
## this project can check from the development machine.
const MAX_AIM_DEGREES: float = 50.0

# Where each badge sits relative to the touched point: four spread across the
# half-circle above it. Nothing goes below, because that is where the player's
# own finger is and it stays down for the whole gesture — which also leaves the
# downward cone free to mean "never mind".
#
# There is deliberately nothing at straight up: with an even number of slices
# laid out symmetrically, the top is always a boundary. Aiming is done at the
# badges, which are visible, so it costs nothing.
const BADGE_OFFSETS: Array = [
	Vector2(-38, -7),
	Vector2(-19, -33),
	Vector2(19, -33),
	Vector2(38, -7),
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

# The words for this opening of the coin, one per slice. Held because the
# badges no longer show them and the caption has to be told what to write.
var _labels: Array[String] = ["", "", "", ""]

# False when the icons could not be loaded, in which case the badges fall back
# to showing the words themselves. A missing picture should cost the pictures,
# not the game.
var _has_icons: bool = true

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
	_build_badges()


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


func close() -> void:
	visible = false
	_hotspot = null
	_item = null
	_highlight(-1)


func _open_at(at_position: Vector2) -> void:
	_anchor = at_position
	_has_left_dead_zone = false
	_place_badges(at_position)
	_highlight(-1)
	visible = true


func _set_label(slice: int, text: String) -> void:
	_labels[slice] = text

	if _has_icons:
		return

	var button: Button = _buttons[slice]
	button.text = text

	# Re-applied straight after the text, and not left to the next layout pass:
	# a longer word raises the button's minimum size, and _place_badges() reads
	# size to work out where the middle of each slice is. Setting it here forces
	# the recalculation now, so what is measured is what will be drawn.
	button.size = FALLBACK_SIZE


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
			_lift()

		get_viewport().set_input_as_handled()


## Answers the finger coming off the glass.
##
## Three outcomes, and the difference between the last two is whether the
## finger ever went anywhere: a tap that stayed put asks for the thing you
## would obviously want, while a drag that ended up pointing at nothing is
## somebody changing their mind.
func _lift() -> void:
	if _highlighted >= 0:
		# The highlighted slice, not a fresh look at where the finger is. In a
		# continuous gesture the state is whatever the interface is showing,
		# and the lift confirms it — it is not an opportunity to work it out
		# again. A fingertip also rolls a pixel or two on its way off the
		# glass, so the two answers need not agree.
		_run(_verbs[_highlighted])
		return

	if not _has_left_dead_zone:
		_run(_default_verb)
		return

	close()


func _run(verb: int) -> void:
	# Closed before the verb goes out, so the coin is gone before anyone reacts
	# to the choice and an action that opens something else does not fight it.
	var hotspot: Hotspot = _hotspot
	var item: InventoryItem = _item
	close()

	if hotspot != null:
		verb_chosen.emit(verb, hotspot)
	elif item != null:
		item_verb_chosen.emit(verb, item)


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
		# Measured against where the badge actually ended up, not against the
		# offset it was asked for: near a screen edge the badges are pushed
		# back inside, and the direction has to follow them there.
		var towards_badge: Vector2 = _buttons[i].get_rect().get_center() - _anchor
		if towards_badge.is_zero_approx():
			continue

		var difference: float = absf(rad_to_deg(aim.angle_to(towards_badge)))
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
		# badge's own two styles, without a second set of art to maintain.
		_buttons[i].button_pressed = i == _highlighted

	aim_changed.emit(_labels[slice] if slice >= 0 else "")


func _build_badges() -> void:
	for i in _default_labels.size():
		var button := Button.new()
		var icon: Texture2D = load(ICON_PATHS[i]) as Texture2D

		if icon == null:
			push_warning("Verb icon missing: %s. Falling back to words." % ICON_PATHS[i])
			_has_icons = false

		button.icon = icon

		# The icon is drawn to the badge's size rather than its own. Without
		# this a 96-pixel drawing would also become the button's minimum size
		# and the coin would fill the screen.
		button.expand_icon = true

		# Overrides the project-wide Nearest filtering, which is there for
		# pixel art and would leave a smooth drawing with jagged edges. These
		# four are the one part of the game that is not pixel art.
		button.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

		button.add_theme_stylebox_override("normal", _badge_style(false))
		button.add_theme_stylebox_override("hover", _badge_style(false))
		button.add_theme_stylebox_override("focus", _badge_style(false))
		button.add_theme_stylebox_override("pressed", _badge_style(true))
		button.add_theme_stylebox_override("hover_pressed", _badge_style(true))
		button.add_theme_font_size_override("font_size", FALLBACK_FONT_SIZE)

		# Nothing here is driven by the keyboard, and a focus ring left behind
		# after the coin closes would be a ghost of a menu that is gone.
		button.focus_mode = Control.FOCUS_NONE

		# Pure visuals: the gesture is read in _input(), so a badge must never
		# intercept an event or decide anything on its own.
		button.mouse_filter = Control.MOUSE_FILTER_IGNORE
		button.toggle_mode = true

		add_child(button)
		_buttons.append(button)

	_resize_badges()


func _badge_style(highlighted: bool) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()

	if highlighted:
		style.bg_color = Color(0.36, 0.32, 0.20)
		style.border_color = Color(0.96, 0.82, 0.36)
		style.set_border_width_all(2)
	else:
		style.bg_color = Color(0.11, 0.12, 0.18, 0.92)
		style.border_color = Color(0.34, 0.36, 0.46)
		style.set_border_width_all(1)

	# Round, not rounded: the radius is half the badge, so the corners meet.
	style.set_corner_radius_all(int(BADGE_SIZE.x * 0.5))

	# The badge is exactly as big as it is drawn. Any content margin would be
	# added to the minimum size and quietly push the badges apart.
	style.set_content_margin_all(0.0)

	return style


func _resize_badges() -> void:
	var wanted: Vector2 = BADGE_SIZE if _has_icons else FALLBACK_SIZE

	for button in _buttons:
		button.custom_minimum_size = wanted
		button.size = wanted


func _place_badges(at_position: Vector2) -> void:
	for i in _buttons.size():
		# The badge's own size, not the constant. A Control refuses to be
		# smaller than the room its content needs, so what is measured here is
		# what will actually be drawn — and the aim is measured against it too.
		var badge_size: Vector2 = _buttons[i].size
		var top_left: Vector2 = at_position + BADGE_OFFSETS[i] - badge_size * 0.5
		_buttons[i].position = _kept_on_screen(top_left, badge_size)


func _kept_on_screen(top_left: Vector2, badge_size: Vector2) -> Vector2:
	var limit: Vector2 = size - badge_size - Vector2(SCREEN_MARGIN, SCREEN_MARGIN)
	return Vector2(
		clampf(top_left.x, SCREEN_MARGIN, limit.x),
		clampf(top_left.y, SCREEN_MARGIN, limit.y)
	)
