extends Node

## State that has to outlive the scene it was created in.
##
## Registered as an autoload, so it exists from launch to quit and is reachable
## as [code]GameState[/code] from any script. Rooms will eventually be loaded
## and unloaded; who the player is controlling must not be loaded and unloaded
## with them, which is the whole reason this exists.
##
## Keep it about state, not behaviour. An autoload is reachable from
## everywhere, and everything it can do is something every script can do.

## Emitted when control passes to another character, and once at startup when
## the first character registers.
signal active_character_changed(character: PlayerCharacter)

## Emitted when a character joins or leaves the roster, so the interface can
## rebuild itself without knowing who did it.
signal roster_changed

## Emitted when a flag is raised, so anything watching for it can react without
## being asked every frame.
signal flag_raised(flag: StringName)

## Every playable character currently in the tree, in registration order.
var characters: Array[PlayerCharacter] = []

## The one the player is controlling. Null only before anyone has registered.
var active_character: PlayerCharacter = null

# What has already happened, as a set of names. A room is thrown away when the
# player leaves it and built again from its scene file when they come back, so
# anything that changed inside it has to be remembered out here or it un-happens
# — a crate emptied would refill itself, and the same item could be taken twice.
#
# Only ever raised, never lowered. That is what a flag is for; a switch that
# can go both ways is state, and state belongs to whatever owns it.
var _flags: Dictionary = {}


## Characters announce themselves as they enter the tree. The alternative —
## a list configured by hand somewhere — would have to be kept in step with
## the scenes, and would drift the first time one is edited.
func register_character(character: PlayerCharacter) -> void:
	if character in characters:
		return

	characters.append(character)
	roster_changed.emit()

	# Whoever turns up first takes control, so a room is playable without
	# anything having to say who starts.
	if active_character == null:
		set_active_character(character)


func unregister_character(character: PlayerCharacter) -> void:
	if not character in characters:
		return

	characters.erase(character)
	roster_changed.emit()

	if active_character == character:
		set_active_character(characters[0] if not characters.is_empty() else null)


func set_active_character(character: PlayerCharacter) -> void:
	if character == active_character:
		return

	active_character = character
	active_character_changed.emit(character)


## True once [param flag] has been raised.
func is_raised(flag: StringName) -> bool:
	return _flags.has(flag)


func raise_flag(flag: StringName) -> void:
	if flag.is_empty() or _flags.has(flag):
		return

	_flags[flag] = true
	flag_raised.emit(flag)
