class_name LocaleTexts
extends Resource

## Every line the game can say, in one language.
##
## One of these per language, under resources/text/. A key like
## ROOM_TEST_CRATE_LOOK appears once here and once wherever the crate is, and
## nothing else in the project holds a sentence.
##
## Why not Godot's own CSV translations, which is the documented road: those are
## *imported* — the editor turns a .csv into .translation files that do not
## exist until somebody opens the project, and they have to be registered in
## project.godot, which the editor rewrites at will. Both halves of that are
## things this project has already been bitten by. A .tres is a resource like
## every other one here: it is exported, it is loaded with load(), it is plain
## text in a diff, and there is no import step between writing it and running.
##
## It is still turned into a real [Translation] and handed to the
## [TranslationServer], so tr() works everywhere and Godot's own automatic
## translation of a Control's text keeps working too.

## The language code, as Godot spells it: "it", "en".
@export var locale: String = ""

## key -> line. A Dictionary and not an array of pairs: it is the shape the
## lookup wants, and in a .tres it reads as one line per string.
@export var entries: Dictionary = {}


## Builds the object the TranslationServer actually wants.
func to_translation() -> Translation:
	var translation := Translation.new()
	translation.locale = locale

	for key in entries:
		translation.add_message(StringName(key), String(entries[key]))

	return translation
