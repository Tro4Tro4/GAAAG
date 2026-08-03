class_name TitleScreen
extends Control

## The front of the game.
##
## An overlay on top of the running game rather than a scene of its own, which
## is the whole trick: there is no scene change, so nothing has to be carried
## across one. Main.tscn boots as it always did, the first room is built
## underneath, and this sits over it until somebody chooses. "Continua" can then
## load a save into a game that is already standing up, instead of having to
## start one and tell it what to become.
##
## It also keeps the decision that Main.tscn is the one scene to press Play on.

## Emitted with one of the constants below.
signal action_chosen(action: StringName)

const CONTINUE: StringName = &"continue"
const NEW_GAME: StringName = &"new_game"
const SETTINGS: StringName = &"settings"
const QUIT: StringName = &"quit"

const FONT_SIZE: int = 8
const ENTRY_MINIMUM_SIZE: Vector2 = Vector2(0, 16)

## Set before the scene is reloaded to say that the player has already chosen,
## and the title must not ask again.
##
## A static, so that it outlives the reload — it belongs to the script, not to
## any node in the tree. It is here and not in an autoload because it is not
## state of the game nor a setting: it is one instruction from the scene that
## is going away to the one taking its place, and it is consumed on arrival.
static var skip_once: bool = false

# The menu, in order. Continua is first because it is what somebody coming back
# wants, and it is the one entry that is not always there.
var _entries: Array = [
	{&"action": CONTINUE, &"text": "TITLE_CONTINUE"},
	{&"action": NEW_GAME, &"text": "MENU_NEW_GAME"},
	{&"action": SETTINGS, &"text": "MENU_SETTINGS"},
	{&"action": QUIT, &"text": "MENU_QUIT"},
]

@onready var _entry_list: VBoxContainer = $Entries


func _ready() -> void:
	visible = false


## Whether the title should be shown at all this time round.
static func should_ask() -> bool:
	var asked: bool = not skip_once
	skip_once = false
	return asked


func open() -> void:
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

		# Everything is swallowed: the game is running underneath, and a tap
		# that got through would send somebody walking behind the title.
		get_viewport().set_input_as_handled()

		if not button_event.pressed or button_event.button_index != MOUSE_BUTTON_LEFT:
			return

		var action: StringName = _entry_at(button_event.position)

		if action != &"":
			action_chosen.emit(action)


func _entry_at(point: Vector2) -> StringName:
	for child in _entry_list.get_children():
		var entry := child as Button
		if entry != null and entry.get_global_rect().has_point(point):
			return entry.get_meta(&"action", &"") as StringName

	return &""


func _build() -> void:
	for child in _entry_list.get_children():
		_entry_list.remove_child(child)
		child.queue_free()

	for entry in _entries:
		# No saves yet, no Continua. An entry that would answer "there is
		# nothing to load" is worse than an entry that is not there.
		if entry[&"action"] == CONTINUE and not _anything_to_continue():
			continue

		_entry_list.add_child(_make_entry(entry))


func _anything_to_continue() -> bool:
	return SaveGame.exists(SaveGame.MANUAL_SLOT) or SaveGame.exists(SaveGame.AUTO_SLOT)


func _make_entry(entry: Dictionary) -> Button:
	var button := Button.new()
	button.text = tr(entry[&"text"])
	button.custom_minimum_size = ENTRY_MINIMUM_SIZE
	button.add_theme_font_size_override("font_size", FONT_SIZE)
	button.focus_mode = Control.FOCUS_NONE
	button.mouse_filter = Control.MOUSE_FILTER_IGNORE
	button.set_meta(&"action", entry[&"action"])

	return button
