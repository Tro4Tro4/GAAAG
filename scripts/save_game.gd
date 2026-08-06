class_name SaveGame
extends RefCounted

## Writes a game out to a file and reads one back.
##
## Soli metodi statici, like [Conditions]: there is nothing to draw and nothing
## to keep between calls. The two halves of the job are split on purpose — the
## pieces that own state know how to hand it over ([method GameState.capture],
## [method PlayerCharacter.capture]) and this knows the things they must not:
## what a file looks like, which version it is, and that a file can hold an
## item's id but never the item.
##
## The format is a [ConfigFile], the ini-like one Godot ships with. Chosen over
## JSON because it keeps Godot's own types: a Vector2 goes out and comes back a
## Vector2, with no pulling apart into two floats and no rebuilding, and every
## conversion avoided is a conversion that cannot be wrong. Chosen over a binary
## dump because a save you cannot open and read is a save you cannot debug —
## which matters more than usual when the machine and the test device are the
## same phone.

## Bumped whenever the shape below changes — and whenever the world it describes
## moves out from under it, which is the same problem wearing different clothes.
## A saved position is only meaningful against the floor it was standing on: when
## a room's navigation mesh moves, every older save puts somebody inside a wall,
## and somebody off the mesh gets no path and never walks again. That is a soft
## lock, and a soft lock is worth a version.
##
## A file from another version is refused rather than migrated: during
## development saves are disposable, and a migration written blind is worse than
## an honest refusal.
##
## 2: the floors of the lobby and of the pipe corridor moved (y=150 to 140 and
##    y=110 to 138), so positions written before that no longer stand on them.
## 3: the base resolution went to 320x180 and every room was re-laid out; the
##    three retired test rooms were deleted, along with four items that nothing
##    could give out any more. A save naming a room that no longer exists loads
##    into an empty RoomContainer -- no navigation region, so nobody walks --
##    which is the same soft lock by another route.
const VERSION: int = 3

## The slot the menu writes to.
const MANUAL_SLOT: StringName = &"manual"

## The slot the game writes to by itself. Kept apart from the manual one so that
## walking through a door can never overwrite a game somebody chose to keep.
const AUTO_SLOT: StringName = &"auto"


static func path_for(slot: StringName) -> String:
	# user:// and not res://: the project folder is read-only once the game is
	# exported, and on a phone it is inside the package.
	return "user://save_%s.cfg" % slot


static func exists(slot: StringName) -> bool:
	return FileAccess.file_exists(path_for(slot))


## True when [param slot] holds a save this build will actually read.
##
## Asked instead of [method exists] by anything that offers to load, because a
## file that is there and a file that can be read stopped being the same thing
## the moment the version could refuse one: an entry that answers "that save is
## from another version" is worse than an entry that is not there, which is the
## rule "Continua" was written to already.
static func is_loadable(slot: StringName) -> bool:
	if not exists(slot):
		return false

	var file := ConfigFile.new()
	if file.load(path_for(slot)) != OK:
		return false

	return int(file.get_value("meta", "version", 0)) == VERSION


## The slot last written to, or empty if neither has been. What "Continua"
## means: the game you were in, whether you asked for it to be kept or the game
## kept it for you.
static func newest_slot() -> StringName:
	# Only a slot this build can read counts as a candidate. Otherwise the newer
	# of the two could be a file from another version, and "Continua" would pick
	# it precisely because it is the most recent thing that cannot be loaded.
	var manual: bool = is_loadable(MANUAL_SLOT)
	var auto: bool = is_loadable(AUTO_SLOT)

	if not manual and not auto:
		return &""

	if not auto:
		return MANUAL_SLOT

	if not manual:
		return AUTO_SLOT

	var manual_time: int = FileAccess.get_modified_time(path_for(MANUAL_SLOT))
	var auto_time: int = FileAccess.get_modified_time(path_for(AUTO_SLOT))

	# A tie goes to the manual one: if both were written in the same second, the
	# one somebody chose is the one they meant.
	return AUTO_SLOT if auto_time > manual_time else MANUAL_SLOT


## Writes the game as it stands into [param slot]. True when it got there.
static func write(slot: StringName) -> bool:
	var file := ConfigFile.new()
	file.set_value("meta", "version", VERSION)

	var world: Dictionary = GameState.capture()
	file.set_value("world", "flags", world[&"flags"])
	file.set_value("world", "switches", world[&"switches"])
	file.set_value("world", "caches", _ids_by_cache(world[&"caches"]))

	for character in GameState.characters:
		var data: Dictionary = character.capture()

		# Keyed by node name, which is the same handle the "who:" condition uses
		# and for the same reason: the displayed name is text that may yet be
		# translated, the node name is an identifier.
		file.set_value("characters", String(character.name), {
			"room": data[&"room"],
			"position": data[&"position"],
			"inventory": _ids_of(data[&"inventory"]),
		})

	if GameState.active_character != null:
		# In meta and not among the characters, so that nobody can name a
		# character "active" and quietly lose them.
		file.set_value("meta", "active", String(GameState.active_character.name))

	var error: int = file.save(path_for(slot))

	if error != OK:
		push_error("Could not write the save to %s (error %d)." % [path_for(slot), error])
		return false

	return true


## Reads [param slot] back into the running game. True when it was read.
##
## Puts the world and the characters back but does not touch the room on
## screen: whoever calls this has to build it again afterwards, because the
## hotspots in it were made for a world that no longer exists.
static func restore(slot: StringName, catalogue: ItemCatalogue) -> bool:
	var file := ConfigFile.new()
	var error: int = file.load(path_for(slot))

	if error != OK:
		push_warning("No save to read at %s (error %d)." % [path_for(slot), error])
		return false

	var version: int = int(file.get_value("meta", "version", 0))
	if version != VERSION:
		push_warning("Save at %s is version %d and this game reads version %d." % [
			path_for(slot), version, VERSION
		])
		return false

	GameState.restore(
		file.get_value("world", "flags", []),
		file.get_value("world", "switches", {}),
		_caches_from_ids(file.get_value("world", "caches", {}), catalogue)
	)

	for character in GameState.characters:
		var key: String = String(character.name)

		if not file.has_section_key("characters", key):
			# Not fatal: a character added to the game after this save was
			# written simply stays where their scene put them.
			push_warning("The save has nothing about %s; leaving them as they are." % key)
			continue

		var data: Dictionary = file.get_value("characters", key, {})

		character.restore(
			String(data.get("room", character.current_room)),
			data.get("position", character.global_position) as Vector2,
			_items_from_ids(data.get("inventory", []), catalogue)
		)

	var active: String = String(file.get_value("meta", "active", ""))
	for character in GameState.characters:
		if String(character.name) == active:
			GameState.set_active_character(character)

	return true


static func _ids_of(items: Array) -> Array:
	var ids: Array = []

	for item in items:
		if item is InventoryItem:
			ids.append(String((item as InventoryItem).id))

	return ids


static func _items_from_ids(ids: Array, catalogue: ItemCatalogue) -> Array[InventoryItem]:
	var items: Array[InventoryItem] = []

	if catalogue == null:
		push_error("No item catalogue: everything anybody was carrying is lost.")
		return items

	for id in ids:
		var item: InventoryItem = catalogue.find(StringName(id))

		if item == null:
			# Loud, because the alternative is a puzzle that cannot be solved
			# and no clue as to why.
			push_error("The catalogue has no item with id '%s'; it is gone from this save." % id)
			continue

		items.append(item)

	return items


static func _ids_by_cache(caches: Dictionary) -> Dictionary:
	var ids: Dictionary = {}

	for cache_id in caches:
		ids[String(cache_id)] = _ids_of(caches[cache_id])

	return ids


static func _caches_from_ids(ids: Dictionary, catalogue: ItemCatalogue) -> Dictionary:
	var caches: Dictionary = {}

	for cache_id in ids:
		# Handed back untyped, which is how GameState keeps them: a typed array
		# put into a Dictionary does not reliably come out typed, and that note
		# is already written where the caches live.
		var contents: Array = []
		contents.assign(_items_from_ids(ids[cache_id], catalogue))
		caches[StringName(cache_id)] = contents

	return caches
