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

## The same for a switch, and the twin of the signal above rather than a
## variation on it: a hotspot that is only there while a door stands open has to
## hear about the door being shut just as much as about it being opened, so this
## one carries the new value.
signal switch_changed(switch: StringName, on: bool)

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

# Items left in a passage and not yet collected, keyed by the passage's name.
# This is where an object lives between one character posting it through a slot
# and another taking it out on the far side: it belongs to nobody in the
# meantime, so it can be in neither inventory and in no room.
#
# The arrays are kept untyped on purpose. A typed array put into a Dictionary
# comes back out as a plain Variant, and this project cannot check from the
# development machine how strict GDScript is about handing it back; the copy
# returned by cache_contents() is typed, which is where it matters.
var _caches: Dictionary = {}

# Things that can go back the way they came: a door open or shut, a lever up or
# down. Deliberately not mixed in with the flags — a flag records that
# something happened and can never un-happen, and not being able to undo it is
# half of what makes it worth trusting.
#
# It lives here for the same reason the flags do: a room is rebuilt from its
# scene file every time it comes back on screen, so anything it changed about
# itself has to be remembered somewhere that outlives it. This is the first
# piece of that, and the wider question of what else a room must remember is
# still open.
var _switches: Dictionary = {}


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


## What is waiting in the passage called [param cache_id], as a copy.
func cache_contents(cache_id: StringName) -> Array[InventoryItem]:
	var contents: Array[InventoryItem] = []

	if _caches.has(cache_id):
		contents.assign(_caches[cache_id])

	return contents


func cache_is_empty(cache_id: StringName) -> bool:
	return cache_contents(cache_id).is_empty()


## Leaves [param item] in the passage called [param cache_id].
func put_in_cache(cache_id: StringName, item: InventoryItem) -> void:
	if cache_id.is_empty() or item == null:
		return

	if not _caches.has(cache_id):
		_caches[cache_id] = []

	var contents: Array = _caches[cache_id]
	if not item in contents:
		contents.append(item)


## Takes everything out of [param cache_id] and returns it.
func empty_cache(cache_id: StringName) -> Array[InventoryItem]:
	var taken: Array[InventoryItem] = cache_contents(cache_id)
	_caches.erase(cache_id)
	return taken


## True when the two-way switch [param switch] is currently on.
func is_on(switch: StringName) -> bool:
	return _switches.get(switch, false)


func set_switch(switch: StringName, on: bool) -> void:
	if switch.is_empty():
		return

	# Nothing is announced when nothing changed. Going through a shut door opens
	# it on the way and going through an open one sets it open again, so without
	# this every walk through a doorway would tell the whole room to rethink
	# itself for no reason.
	if _switches.get(switch, false) == on:
		return

	_switches[switch] = on
	switch_changed.emit(switch, on)


## True once [param flag] has been raised.
func is_raised(flag: StringName) -> bool:
	return _flags.has(flag)


func raise_flag(flag: StringName) -> void:
	if flag.is_empty() or _flags.has(flag):
		return

	_flags[flag] = true
	flag_raised.emit(flag)
