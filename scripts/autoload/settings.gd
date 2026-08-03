extends Node

## What the player chose, as opposed to what the player did.
##
## The second autoload, and kept apart from GameState on purpose: GameState is
## one playthrough and is written into a saved game, while this outlives every
## playthrough and has a file of its own. Loading a save must never change the
## language, and starting a new game must never reset the volume.
##
## It does one thing besides holding values, and it is the reason it is an
## autoload rather than a resource somebody loads: the languages have to be
## installed in the TranslationServer before anything draws a single word, and
## an autoload is the only place that runs before every scene.

## Emitted after the language has changed, for the parts of the interface that
## have already turned a key into a sentence and cannot do it again by
## themselves — buttons built in code, mostly.
signal locale_changed

const PATH: String = "user://settings.cfg"

## Used when there is no settings file and the system language is not one the
## game speaks. Italian because that is the language the game is written in.
const DEFAULT_LOCALE: String = "it"

## The languages the game speaks, and where each one's lines live. Adding a
## language is a row here and a file next to the others.
var _locale_files: Dictionary = {
	"it": "res://resources/text/it.tres",
	"en": "res://resources/text/en.tres",
}

## The names the languages call themselves. Never translated — a language
## picker that says "Italian" to somebody who only reads Italian is no use.
var _locale_names: Dictionary = {
	"it": "Italiano",
	"en": "English",
}

var locale: String = DEFAULT_LOCALE


func _ready() -> void:
	_install_translations()
	_read()
	TranslationServer.set_locale(locale)


## The language codes the game speaks, in a fixed order.
func available_locales() -> PackedStringArray:
	var codes: PackedStringArray = PackedStringArray()

	for code in _locale_files:
		codes.append(String(code))

	return codes


## What [param code] calls itself, for a language picker.
func name_of(code: String) -> String:
	return String(_locale_names.get(code, code))


## Switches language and remembers the choice.
func set_locale(code: String) -> void:
	if code == locale or not _locale_files.has(code):
		return

	locale = code
	TranslationServer.set_locale(code)
	write()
	locale_changed.emit()


func write() -> void:
	var file := ConfigFile.new()
	file.set_value("player", "locale", locale)

	var error: int = file.save(PATH)
	if error != OK:
		push_warning("Could not write the settings to %s (error %d)." % [PATH, error])


func _read() -> void:
	var file := ConfigFile.new()

	if file.load(PATH) != OK:
		# No settings yet: follow the machine if the game speaks its language,
		# and fall back to the one it was written in if it does not.
		var system: String = OS.get_locale_language()
		locale = system if _locale_files.has(system) else DEFAULT_LOCALE
		return

	var stored: String = String(file.get_value("player", "locale", DEFAULT_LOCALE))
	locale = stored if _locale_files.has(stored) else DEFAULT_LOCALE


func _install_translations() -> void:
	for code in _locale_files:
		var texts: LocaleTexts = load(_locale_files[code]) as LocaleTexts

		if texts == null:
			# Loud: without this the whole game shows keys instead of words,
			# which looks like a hundred bugs rather than one missing file.
			push_error("Could not load the %s texts from %s." % [code, _locale_files[code]])
			continue

		TranslationServer.add_translation(texts.to_translation())
