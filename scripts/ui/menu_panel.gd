class_name MenuPanel
extends Control

## Save, load, start again.
##
## The first piece of the shell around the game — there is no title screen and
## no pause yet — and it exists now because a save nobody can ask for cannot be
## tested. It is built to grow into the pause menu rather than to be thrown
## away: the entries are a table, and settings will be another row.
##
## Input is read raw in _input() with the buttons left as visuals, as in the
## other three panels. Tapping outside puts it away, exactly as the bag does.

## Emitted with one of the four constants below. Nothing is emitted when the
## panel is simply dismissed: unlike the bag, which leaves half a sentence in
## somebody's hand, a menu closed without choosing has changed nothing.
signal action_chosen(action: StringName)

const SAVE: StringName = &"save"
const LOAD: StringName = &"load"
const LOAD_AUTO: StringName = &"load_auto"
const NEW_GAME: StringName = &"new_game"

const ENTRY_FONT_SIZE: int = 8
const ENTRY_MINIMUM_SIZE: Vector2 = Vector2(0, 14)

# The menu, in order. A table and not four hand-placed buttons: the next entry
# is a row here rather than a node, a signal and a scene edit.
var _entries: Array = [
	{&"action": SAVE, &"text": "MENU_SAVE"},
	{&"action": LOAD, &"text": "MENU_LOAD"},
	{&"action": LOAD_AUTO, &"text": "MENU_LOAD_AUTO"},
	{&"action": NEW_GAME, &"text": "MENU_NEW_GAME"},
]

@onready var _frame: Panel = $Frame
@onready var _list: VBoxContainer = $Frame/Entries


func _ready() -> void:
	visible = false


func open() -> void:
	# Built on the way up rather than once at startup, so that a change of
	# language is picked up without anybody having to be told about it.
	_build()
	visible = true


func close() -> void:
	visible = false


func is_open() -> bool:
	return visible


func _input(event: InputEvent) -> void:
	if not visible:
		return

	if event is InputEventMouseButton:
		var button_event: InputEventMouseButton = event

		# Everything is swallowed while the menu is up, both directions of every
		# button. A menu that lets a stray release through to the room would
		# order a walk from behind itself.
		get_viewport().set_input_as_handled()

		if not button_event.pressed or button_event.button_index != MOUSE_BUTTON_LEFT:
			return

		# Read straight from the event, with no conversion. See the note at the
		# top of verb_coin.gd.
		var action: StringName = _entry_at(button_event.position)

		if action != &"":
			close()
			action_chosen.emit(action)
		elif not _frame.get_global_rect().has_point(button_event.position):
			close()


func _entry_at(point: Vector2) -> StringName:
	for child in _list.get_children():
		var entry := child as Button
		if entry != null and entry.get_global_rect().has_point(point):
			return entry.get_meta(&"action", &"") as StringName

	return &""


func _build() -> void:
	for child in _list.get_children():
		_list.remove_child(child)
		child.queue_free()

	for entry in _entries:
		var button := Button.new()
		button.text = tr(entry[&"text"])
		button.custom_minimum_size = ENTRY_MINIMUM_SIZE
		button.add_theme_font_size_override("font_size", ENTRY_FONT_SIZE)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.focus_mode = Control.FOCUS_NONE
		button.mouse_filter = Control.MOUSE_FILTER_IGNORE

		# Metadata, as the inventory slots do: a Button has nowhere else to
		# carry what it stands for, and a parallel array would have to be kept
		# in step with the children of a container.
		button.set_meta(&"action", entry[&"action"])

		_list.add_child(button)
