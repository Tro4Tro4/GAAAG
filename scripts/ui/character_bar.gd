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
	# Rebuilt on a change of language as well as of roster: these buttons hold
	# a name that has already been turned into words, so Godot's own automatic
	# retranslation has nothing left to work on.
	Settings.locale_changed.connect(_rebuild)

	GameState.roster_changed.connect(_rebuild)
	GameState.active_character_changed.connect(_on_active_character_changed)

	# A character can join the party partway through the game, and joining is a
	# flag going up. Both kinds of state change are listened to for the same
	# reason the hotspots listen to them: whoever appears when the world changes
	# has to hear the world change.
	GameState.flag_raised.connect(_on_state_changed)
	GameState.switch_changed.connect(_on_state_changed)

	# Characters register during their own _ready(), which runs before this
	# one, so the roster is already populated and the signals above will not
	# fire for what is already there.
	_rebuild()


func _on_active_character_changed(_character: PlayerCharacter) -> void:
	_rebuild()


# Both signals carry an argument this does not care about, and one of them
# carries two. Written out rather than bound away: a bar that rebuilt itself
# only for some kinds of change would be a bug waiting for the first switch.
func _on_state_changed(_a = null, _b = null) -> void:
	_rebuild()


func _rebuild() -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()

	for character in GameState.characters:
		# Everyone is always on the roster and always alive somewhere. Whether
		# they are offered is a separate question, and the character answers it.
		if not character.is_available():
			continue

		add_child(_make_button(character))


func _make_button(character: PlayerCharacter) -> Button:
	var button := Button.new()
	button.text = tr(character.display_name)
	button.add_theme_font_size_override("font_size", BUTTON_FONT_SIZE)

	# Nothing in this game is driven by the keyboard, and a button keeping
	# focus would draw a focus ring nobody asked for.
	button.focus_mode = Control.FOCUS_NONE

	# The character already in control is the one button that does nothing;
	# greying it out says so without needing a highlight of its own.
	button.disabled = character == GameState.active_character

	button.pressed.connect(GameState.set_active_character.bind(character))
	return button
