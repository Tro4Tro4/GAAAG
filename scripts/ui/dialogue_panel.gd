class_name DialoguePanel
extends Control

## The list of things the player may say, along the bottom of the screen.
##
## A plain list and not a ring of slices like the verb-coin. The coin works
## because its vocabulary is closed and its four positions never move, so it can
## be aimed at without being read; a conversation is the exact opposite — the
## options are sentences, they are different every time, and there is no
## learning where they are. So they are read, and a list is what gets read.
##
## The panel is modal while it is up: every mouse button event is swallowed,
## which is what stops the room walking somebody across the screen behind an
## open conversation. Nothing has to be told to be quiet — the room listens in
## _unhandled_input, and an event marked handled here never gets that far. That
## also takes the switch bar and the bag button out of service, which is right:
## you cannot wander off in the middle of being talked at.
##
## Input is read raw in _input() and the option buttons are visuals with
## MOUSE_FILTER_IGNORE, exactly as in InventoryPanel and VerbCoin. Here the
## reason is only consistency — there is no gesture to start on the way down —
## but three panels answering clicks three different ways would be worse than
## one of them being slightly more careful than it needs to be.

## Emitted when the player says the option at [param index] of the last set
## given to [method show_options].
signal option_selected(index: int)

const OPTION_FONT_SIZE: int = 8

## Wide enough is settled by the frame; tall enough is not, because a Control
## refuses to be smaller than its content and a themed Button is taller than its
## text. Fourteen is the smallest that has room for a line of font size 8.
const OPTION_MINIMUM_SIZE: Vector2 = Vector2(0, 14)

@onready var _frame: Panel = $Frame
@onready var _options: VBoxContainer = $Frame/Options


func _ready() -> void:
	visible = false


## Puts [param texts] on screen as the things that may be said.
func show_options(texts: PackedStringArray) -> void:
	_rebuild(texts)
	visible = true


func close() -> void:
	visible = false

	# Emptied on the way out rather than on the way in: a panel that keeps the
	# last conversation's options while hidden would flash them for a frame at
	# the start of the next one.
	_rebuild(PackedStringArray())


func is_open() -> bool:
	return visible


func _input(event: InputEvent) -> void:
	if not visible:
		return

	if event is InputEventMouseButton:
		var button_event: InputEventMouseButton = event

		# Marked handled whichever button it was and whichever way it was going.
		# Half a modal panel is worse than none: letting the release through
		# would be enough for a stray tap to reach the room underneath.
		get_viewport().set_input_as_handled()

		if button_event.pressed and button_event.button_index == MOUSE_BUTTON_LEFT:
			# Straight from the event, with no conversion. See the note at the
			# top of verb_coin.gd for what make_input_local() does to this.
			var index: int = _option_at(button_event.position)

			if index >= 0:
				option_selected.emit(index)


## The position in the list of the option under [param point], or -1. Global
## rects: the buttons sit in a container inside the frame, so their own position
## is relative to the container and says nothing about where they are on screen.
func _option_at(point: Vector2) -> int:
	var index: int = 0

	for child in _options.get_children():
		var option := child as Button
		if option != null:
			if option.get_global_rect().has_point(point):
				return index
			index += 1

	return -1


func _rebuild(texts: PackedStringArray) -> void:
	for child in _options.get_children():
		_options.remove_child(child)
		child.queue_free()

	for text in texts:
		_options.add_child(_make_option(text))


func _make_option(text: String) -> Button:
	var option := Button.new()
	option.text = text
	option.custom_minimum_size = OPTION_MINIMUM_SIZE
	option.add_theme_font_size_override("font_size", OPTION_FONT_SIZE)
	option.alignment = HORIZONTAL_ALIGNMENT_LEFT
	option.focus_mode = Control.FOCUS_NONE
	option.mouse_filter = Control.MOUSE_FILTER_IGNORE

	return option
