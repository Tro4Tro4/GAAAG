class_name Conditions
extends RefCounted

## Whether something is true of the game right now, written as a short string.
##
## Shared on purpose. Rooms need it to decide whether a hotspot is there and
## what it has to say; dialogues will need the same thing to decide which lines
## the player may choose. Two separate ways of writing "only if..." would be two
## grammars to learn and two evaluators to keep in step.
##
## A condition is a string, not a resource with typed fields. The reason is that
## a flag in this project is already a string everywhere — [member
## Hotspot.accepted_flag], [member DoorHotspot.state_id], [member
## PassageHotspot.cache_id] are all StringNames written by hand, and
## PickupHotspot builds "taken:" + item.id by itself. A typed version would buy
## safety on one of the six kinds below and cost a block of sub-resource on all
## of them, in a project whose scenes are written as text.
##
## Accepted cost, and there is no way around it: a misspelt name is not
## reported. "taken:stiker" is a perfectly well-formed condition about a flag
## nobody will ever raise, and so is "hass:key". Only an empty argument is
## caught, because that one is always a mistake.
##
## The grammar, in full:
## [codeblock]
## taken:sticker    a flag by that name has been raised
## !taken:sticker   ...has not
## on:hallway_door  a two-way switch is on
## has:screwdriver  the character is carrying the item with that id
## in:wall_slot     something is waiting in that passage
## who:Player2      that character is the one being controlled
## [/codeblock]
##
## Anything without a known prefix is a flag name — which is why flags may
## contain colons of their own and "taken:sticker" needs no prefix at all.
##
## A list of conditions is an AND. There is no OR and no nesting: for an OR you
## write the entry twice, which keeps the data flat and readable instead of
## turning it into a boolean tree nobody can follow six months later.
##
## Note for the C# side of the brain: GDScript has no static classes, so this is
## an ordinary class whose methods are all [code]static[/code]. Nothing is ever
## instantiated — it is called as [code]Conditions.all_hold(...)[/code].

const NEGATION: String = "!"

const SWITCH_PREFIX: String = "on:"
const ITEM_PREFIX: String = "has:"
const CACHE_PREFIX: String = "in:"
const CHARACTER_PREFIX: String = "who:"


## True when every condition in [param conditions] holds. An empty list holds:
## a hotspot with nothing written in it is simply always there.
static func all_hold(conditions: PackedStringArray, character: PlayerCharacter) -> bool:
	for condition in conditions:
		if not holds(condition, character):
			return false

	return true


## True when the single condition [param condition] holds.
static func holds(condition: String, character: PlayerCharacter) -> bool:
	var text: String = condition.strip_edges()

	if text.is_empty():
		return true

	var negated: bool = text.begins_with(NEGATION)
	if negated:
		text = text.substr(NEGATION.length()).strip_edges()

	# != on two bools is exclusive-or: the test, flipped when it was negated.
	return _test(text, character) != negated


static func _test(text: String, character: PlayerCharacter) -> bool:
	if text.begins_with(SWITCH_PREFIX):
		return GameState.is_on(StringName(_argument(text, SWITCH_PREFIX)))

	if text.begins_with(ITEM_PREFIX):
		return _is_carrying(character, StringName(_argument(text, ITEM_PREFIX)))

	if text.begins_with(CACHE_PREFIX):
		return not GameState.cache_is_empty(StringName(_argument(text, CACHE_PREFIX)))

	if text.begins_with(CHARACTER_PREFIX):
		# Matched against the node name and not the display name: the name shown
		# to the player is a piece of text that may yet be translated, while the
		# node name is an identifier and stays put.
		return character != null and String(character.name) == _argument(text, CHARACTER_PREFIX)

	return GameState.is_raised(StringName(text))


## By id rather than by an InventoryItem reference, so that a condition stays a
## single string. The id is the item's identity anyway — it is what
## PickupHotspot already builds its flag out of.
static func _is_carrying(character: PlayerCharacter, item_id: StringName) -> bool:
	if character == null or item_id.is_empty():
		return false

	for item in character.inventory:
		if item != null and item.id == item_id:
			return true

	return false


static func _argument(text: String, prefix: String) -> String:
	var argument: String = text.substr(prefix.length()).strip_edges()

	# The one mistake worth reporting. A name that is merely wrong cannot be
	# told from a name that has not been raised yet, but a name that is not
	# there at all is never anything but a slip.
	if argument.is_empty():
		push_warning("Condition '%s' names nothing after '%s'." % [text, prefix])

	return argument
