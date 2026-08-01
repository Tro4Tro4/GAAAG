extends HBoxContainer

## The row of buttons that passes control from one character to another.
##
## Built from the roster at runtime instead of being laid out by hand: the bar
## then follows however many characters a room happens to have, and there is
## no second list to keep in step with the scenes.
##
## Being made of Control nodes, it also consumes its own clicks before the
## room sees them — which is exactly why the room listens on _unhandled_input
## rather than _input.

## Font size for the buttons, at the game's 384x216 base resolution. The
## default is sized for ordinary screens and would be enormous here.
const BUTTON_FONT_SIZE: int = 8


func _ready() -> void:
	GameState.roster_changed.connect(_rebuild)
	GameState.active_character_changed.connect(_on_active_character_changed)

	# Characters register during their own _ready(), which runs before this
	# one, so the roster is already populated and the signals above will not
	# fire for what is already there.
	_rebuild()


func _on_active_character_changed(_character: PlayerCharacter) -> void:
	_rebuild()


func _rebuild() -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()

	for character in GameState.characters:
		add_child(_make_button(character))


func _make_button(character: PlayerCharacter) -> Button:
	var button := Button.new()
	button.text = character.display_name
	button.add_theme_font_size_override("font_size", BUTTON_FONT_SIZE)

	# Nothing in this game is driven by the keyboard, and a button keeping
	# focus would draw a focus ring nobody asked for.
	button.focus_mode = Control.FOCUS_NONE

	# The character already in control is the one button that does nothing;
	# greying it out says so without needing a highlight of its own.
	button.disabled = character == GameState.active_character

	button.pressed.connect(GameState.set_active_character.bind(character))
	return button
