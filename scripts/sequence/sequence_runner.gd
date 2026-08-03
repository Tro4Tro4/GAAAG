class_name SequenceRunner
extends Node

## Plays a [Sequence], one step at a time, waiting for each.
##
## A Node and not a plain object, unlike [DialogueRunner]: a conversation waits
## for the player and can afford to be a bag of state that somebody pokes, while
## a scene waits for time and for a walk to finish. Waiting needs a tree — a
## timer comes from one — so this has to be in it.
##
## Written with await rather than as a state machine with a step index. The
## whole point of a sequence is that it reads in order, and await is the one
## thing in GDScript that lets code be written in the order it happens. Note for
## the C# side of the brain: this is the same await, but there are no threads
## anywhere near it and nothing to configure — the function simply stops and is
## resumed by a signal.

## Emitted when the scene is over, however it ended.
signal finished

## Emitted for each line the scene says. Whoever is listening puts it on screen
## and, more importantly, decides how long a line takes to read.
signal wants_to_say(text: String)

## Emitted for each noise it makes.
signal wants_to_play(sound: AudioStream)

## How long a spoken line is left up before the next step is asked of the
## caption rather than guessed, so that a scene keeps pace with whatever reading
## speed the player has chosen.
##
## Handed over by Game rather than exported: a node reference written by hand
## into a .tscn is not reliably resolved in this project, which is why nothing
## here uses @export for one.
var caption: Caption = null

var _running: bool = false


func is_running() -> bool:
	return _running


## Plays [param sequence] with [param character] as the one it happens to, in
## [param room] — which is what names like "in front of the machine" are
## resolved against.
func run(sequence: Sequence, character: PlayerCharacter, room: Room) -> void:
	if sequence == null or sequence.steps.is_empty():
		# Finished all the same, so that whoever put the interface away for this
		# gets it back. A scene too empty to play is still a scene that is over.
		finished.emit()
		return

	_running = true

	for step in sequence.steps:
		if step != null:
			await _play(step, character, room)

	_running = false
	finished.emit()


func _play(step: SequenceStep, character: PlayerCharacter, room: Room) -> void:
	match step.kind:
		SequenceStep.Kind.SAY:
			wants_to_say.emit(step.text)
			await _pause(_seconds_for(step.text))

		SequenceStep.Kind.WAIT:
			await _pause(step.seconds)

		SequenceStep.Kind.WALK:
			await _walk(step, character, room)

		SequenceStep.Kind.FACE:
			if character != null and room != null:
				character.face_towards(room.get_entry_position(step.point))

		SequenceStep.Kind.SOUND:
			wants_to_play.emit(step.sound)

		SequenceStep.Kind.FLAG:
			GameState.raise_flag(step.name)

		SequenceStep.Kind.SWITCH:
			GameState.set_switch(step.name, step.on)

		SequenceStep.Kind.GIVE:
			if character != null:
				character.take(step.item)

		SequenceStep.Kind.TAKE:
			if character != null:
				character.give_up(step.item)


func _walk(step: SequenceStep, character: PlayerCharacter, room: Room) -> void:
	if character == null or room == null:
		return

	character.walk_to(room.get_entry_position(step.point))

	# The signal and not a fixed wait: how long a walk takes depends on where
	# somebody was standing when the scene began, which is not knowable when it
	# is written.
	await character.destination_reached


func _pause(seconds: float) -> void:
	if seconds <= 0.0:
		return

	await get_tree().create_timer(seconds).timeout


func _seconds_for(text: String) -> float:
	if caption == null:
		return 1.0

	return caption.seconds_for(text)
