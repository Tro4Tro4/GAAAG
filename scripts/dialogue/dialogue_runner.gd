class_name DialogueRunner
extends RefCounted

## Runs one conversation: keeps the place, works out what may be said, applies
## what saying it does.
##
## Not a node. It has nothing to draw and nowhere to be in the scene tree — Game
## holds one for the whole session and wires it to the caption and the panel, so
## the model of a conversation and the look of it never learn about each other.
##
## Note for the C# side of the brain: signals work on any Object, not only on
## nodes, and RefCounted is freed when the last reference to it goes — this is
## the one corner of Godot where lifetime works the way .NET taught you.

## Something has been said. The colour tells the caption whose words these are.
signal said(text: String, color: Color)

## The player may now say any of these, in this order. Their positions are what
## [method choose] takes.
signal offered(texts: PackedStringArray)

## The conversation is over.
signal finished

## How many options the panel shows without crowding. Not a limit: more are
## offered all the same, and this only buys a warning while the conversation is
## being written rather than a discovery on somebody's phone.
const COMFORTABLE_OPTIONS: int = 4

var _dialogue: Dialogue = null
var _line: DialogueLine = null
var _character: PlayerCharacter = null

# The options currently on offer, in the order they were offered. Kept because
# choose() is given a position on screen, and the conditions could be worked out
# differently by then — a flag raised in between would renumber them.
var _available: Array[DialogueOption] = []


func is_running() -> bool:
	return _dialogue != null


## Begins [param dialogue], with [param character] as the one doing the talking.
## Who that is matters: conditions ask what they are carrying and who they are,
## and an option that hands something over hands it to them.
##
## Always ends in one of two ways: either options have been offered, or
## [signal finished] has been emitted. Even a conversation too broken to begin
## finishes, because whoever put the interface aside for it is waiting to be
## told it may come back — and a warning nobody can see would otherwise leave
## the game with no switch bar.
func start(dialogue: Dialogue, character: PlayerCharacter) -> void:
	if dialogue == null or dialogue.lines.is_empty():
		push_warning("Asked to start a conversation that has no lines in it.")
		finished.emit()
		return

	_dialogue = dialogue
	_character = character
	_go_to(dialogue.lines[0])


## Says the option at [param index] of the last set offered.
func choose(index: int) -> void:
	if not is_running() or index < 0 or index >= _available.size():
		return

	var option: DialogueOption = _available[index]

	for flag in option.raises:
		GameState.raise_flag(StringName(flag))

	for switch in option.switches_on:
		GameState.set_switch(StringName(switch), true)

	for switch in option.switches_off:
		GameState.set_switch(StringName(switch), false)

	if _character != null:
		# Taken before given, so that an option which swaps one thing for
		# another cannot briefly leave somebody holding both.
		if option.takes != null:
			_character.give_up(option.takes)

		if option.gives != null:
			_character.take(option.gives)

	if option.ends:
		_say(option.reply)
		_stop()
		return

	if option.goes_to.is_empty():
		# Staying put, so the answer is the option's own. The options are worked
		# out again rather than reused: this option may just have raised the very
		# flag that another one was waiting for, or that hides itself.
		_say(option.reply)
		_offer()
		return

	if not option.reply.is_empty():
		push_warning("Option '%s' has both a reply and a goes_to; only the line it arrives at will be heard." % option.text)

	var destination: DialogueLine = _dialogue.find(option.goes_to)

	if destination == null:
		push_error("Option '%s' leads to '%s', which this conversation has not got." % [option.text, option.goes_to])
		_stop()
		return

	_go_to(destination)


## Ends the conversation wherever it is. Nothing calls this today; it is here
## because a cutscene or a character walking off will one day have to.
func stop() -> void:
	if is_running():
		_stop()


func _go_to(line: DialogueLine) -> void:
	_line = line
	_say(line.says)
	_offer()


func _offer() -> void:
	_available.clear()

	for option in _line.options:
		if option != null and Conditions.all_hold(option.conditions, _character):
			_available.append(option)

	# Nothing left to say is how an ordinary conversation ends: the last line is
	# spoken and that is that. Only a goodbye offered among other options needs
	# to say so with [member DialogueOption.ends].
	if _available.is_empty():
		_stop()
		return

	if _available.size() > COMFORTABLE_OPTIONS:
		push_warning("Line '%s' is offering %d options at once; the panel is built for %d." % [
			_line.id, _available.size(), COMFORTABLE_OPTIONS
		])

	var texts: PackedStringArray = PackedStringArray()
	for option in _available:
		texts.append(option.text)

	offered.emit(texts)


func _say(text: String) -> void:
	if text.is_empty():
		return

	said.emit(text, _dialogue.speaker_color)


func _stop() -> void:
	# Cleared before the signal, so that anything listening finds a runner that
	# is already idle rather than one caught halfway out.
	_dialogue = null
	_line = null
	_character = null
	_available.clear()

	finished.emit()
