class_name SettingsPanel
extends Control

## What the player can change about the game rather than in it.
##
## Only the language for now. It is a panel and not a screen because it is
## wanted from two places — the title and the pause menu — and a panel can be
## put over either of them without either knowing.
##
## Every row is built in code from what [Settings] offers, so adding a language
## is a line in Settings and nothing here.

## Nothing is emitted when it closes: whoever opened it is still there
## underneath — the title if it came from the title, the game if it came from
## the pause menu — and neither has anything to do about it.

const FONT_SIZE: int = 8
const ROW_MINIMUM_SIZE: Vector2 = Vector2(0, 14)

@onready var _frame: Panel = $Frame
@onready var _languages: VBoxContainer = $Frame/Languages


func _ready() -> void:
	visible = false


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
		get_viewport().set_input_as_handled()

		if not button_event.pressed or button_event.button_index != MOUSE_BUTTON_LEFT:
			return

		var code: String = _language_at(button_event.position)

		if not code.is_empty():
			# Settings does the remembering and the announcing; this only asks.
			Settings.set_locale(code)

			# Rebuilt on the spot: the buttons carry words that have already
			# been chosen, so the panel would otherwise go on offering the old
			# language's spelling of the new language's name.
			_build()
			return

		if not _frame.get_global_rect().has_point(button_event.position):
			close()


func _language_at(point: Vector2) -> String:
	for child in _languages.get_children():
		var row := child as Button
		if row != null and row.get_global_rect().has_point(point):
			return String(row.get_meta(&"locale", ""))

	return ""


func _build() -> void:
	for child in _languages.get_children():
		_languages.remove_child(child)
		child.queue_free()

	for code in Settings.available_locales():
		_languages.add_child(_make_row(code))


func _make_row(code: String) -> Button:
	var row := Button.new()

	# The language's own name for itself, never translated: "Italiano" written
	# in English is no help to somebody who is looking for Italian.
	row.text = Settings.name_of(code)

	row.custom_minimum_size = ROW_MINIMUM_SIZE
	row.add_theme_font_size_override("font_size", FONT_SIZE)
	row.alignment = HORIZONTAL_ALIGNMENT_LEFT
	row.focus_mode = Control.FOCUS_NONE
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Greyed out rather than ticked: the language already in use is the one row
	# that would do nothing, which is the same thing the switch bar says about
	# the character already in control.
	row.disabled = code == Settings.locale

	row.set_meta(&"locale", code)
	return row
