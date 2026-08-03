class_name Dialogue
extends Resource

## One whole conversation, as a file under resources/dialogues/.
##
## A resource and not a text format with a parser of its own. The runtime eats
## resources, so the day writing these by hand stops scaling — and it will, this
## being the content that grows most — a parser turning a script-like text file
## into one of these can be added without touching a line of DialogueRunner.
## Choosing the writing format now would mean choosing it before a single real
## conversation exists.

## Who is doing the talking, as a colour. The caption is shared with the
## narrator and with every other object in the game, so the colour is what says
## that these words come from somebody rather than from the room.
@export var speaker_color: Color = Color(1, 1, 1)

## The lines, in no particular order except that the first one is where the
## conversation starts. One field fewer to keep in step than naming the opening
## line would be.
@export var lines: Array[DialogueLine] = []


## The line called [param id], or null. Null is a mistake in the data and the
## runner reports it — there is no sensible fallback, since going nowhere and
## going somewhere unintended are both wrong.
func find(id: StringName) -> DialogueLine:
	for line in lines:
		if line != null and line.id == id:
			return line

	return null
