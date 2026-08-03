class_name DialogueLine
extends Resource

## Something said, and everything that may be said back to it.
##
## Called a line and not a node on purpose: in Godot a node is a thing in the
## scene tree, and a conversation has none. This is data.

## How options elsewhere point here. Only has to be unique within its own
## conversation.
@export var id: StringName = &""

## What is said on arriving here. Left empty for a line that only exists to
## offer a fresh set of options.
@export_multiline var says: String = ""

@export var options: Array[DialogueOption] = []
