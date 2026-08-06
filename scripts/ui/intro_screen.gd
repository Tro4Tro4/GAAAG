class_name IntroScreen
extends Control

## The opening of the game: a removal order that fills itself in, line by line,
## and is then stamped.
##
## An overlay over a game that is already standing up, exactly like
## [TitleScreen] and for the same reason — whatever is underneath is already
## built, so nothing has to be told what to become when this is over. The first
## room is already there behind this, which is why the scene that follows can
## start walking somebody about the moment the paper goes away.
##
## Nothing readable is baked into the picture. The paper is paper, rules and
## boxes; every word is a [Label] carrying a key, so the order is written in
## it.tres and en.tres like the rest of the game. Godot translates a Label's
## text by itself when the string is a key the [TranslationServer] knows, which
## is why nothing here calls tr().

## Emitted when the paper has gone away, however it got there.
signal finished

## Emitted for each noise, so the audio director makes it. Same shape as
## [SequenceRunner]: whoever plays sounds is not this node's business.
signal wants_to_play(sound: AudioStream)

## How long each line is left alone before the next one lands. A tap lands the
## next line early rather than skipping the whole thing, which is what a reader
## faster than the default actually wants.
@export var line_seconds: float = 1.6

## The beat on the finished order before the stamp comes down. Longer than a
## line: it is the pause of somebody reading it through before signing.
@export var before_stamp_seconds: float = 1.2

## And how long the stamped order stays up.
@export var after_stamp_seconds: float = 2.4

@export var line_sound: AudioStream = null
@export var stamp_sound: AudioStream = null

@onready var _heading: Label = $Heading
@onready var _lines: VBoxContainer = $Lines
@onready var _stamp: TextureRect = $Stamp

var _running: bool = false

## Set by a press, cleared at the start of every wait. Not a "skip everything"
## flag: it ends the current wait only, so holding still through the whole
## intro and tapping through it both work, and neither has a special case.
var _advance: bool = false


func _ready() -> void:
	hide()
	set_process_input(false)


func is_running() -> bool:
	return _running


## Plays the whole thing. Await it: the function returns when the paper is gone.
func play() -> void:
	if _running:
		return

	_running = true
	_advance = false

	_heading.hide()
	for line in _lines.get_children():
		(line as CanvasItem).hide()
	_stamp.hide()

	show()
	set_process_input(true)

	_reveal(_heading)
	await _pause(line_seconds)

	for line in _lines.get_children():
		_reveal(line as CanvasItem)
		await _pause(line_seconds)

	await _pause(before_stamp_seconds)

	_stamp.show()
	wants_to_play.emit(stamp_sound)
	await _pause(after_stamp_seconds)

	set_process_input(false)
	hide()
	_running = false
	finished.emit()


func _reveal(item: CanvasItem) -> void:
	item.show()
	wants_to_play.emit(line_sound)


## Waits [param seconds], or until the player asks for the next line.
##
## Written as a loop over frames rather than as a race between a timer and a
## signal, because GDScript has no "await whichever of these two happens
## first" and building one costs more than counting.
func _pause(seconds: float) -> void:
	_advance = false

	var elapsed: float = 0.0
	while elapsed < seconds and not _advance:
		await get_tree().process_frame
		elapsed += get_process_delta_time()


func _input(event: InputEvent) -> void:
	# Mouse only, as everywhere else in this project: the engine turns a touch
	# into a mouse event for us, and listening for both would fire twice.
	if event is InputEventMouseButton and event.is_pressed():
		_advance = true
		get_viewport().set_input_as_handled()
