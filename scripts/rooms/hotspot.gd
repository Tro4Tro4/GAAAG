class_name Hotspot
extends Area2D

## A clickable thing in a room: a door, a crate, a panel.
##
## A hotspot carries data, not behaviour. Most of them only need a name, a few
## lines of description and a place to stand — no script of their own. The ones
## that actually do something connect to [signal interacted] or extend this
## class.
##
## An Area2D is used purely as a shape the room can query. The hotspot does
## not listen for its own clicks: the room decides what a click means, so the
## priority between hotspot and floor lives in one place.

## The whole vocabulary of the game. Seven words and no more: a closed list is
## something the player learns once and can then apply everywhere, while words
## invented object by object have to be read every time.
##
## Walking is not among them — you click the floor for that. GO is for a door,
## which is a place you go rather than a stretch of floor you walk on.
##
## PRESS and PULL were here and are gone. They shared the ACT slot with USE, so
## they never bought a position on the coin — only two more words to learn and
## two more lines to write for every hotspot, to say what USE already says.
## What the object does about being used is the text's business, not the verb's.
enum Verb { NONE, LOOK, TAKE, USE, OPEN, CLOSE, TALK, GO }

## The four places on the coin, left to right, and the family of verbs each
## one holds.
##
## A word never changes direction: LOOK is always to the left, anything to do
## with holding is always up-left, anything you do *to* the thing is always
## up-right, and where it leads or who it is is always to the right. That is
## what keeps the gesture aimable without reading — the slice that varies is
## which word of the family is in it, never where the family sits.
##
## Checked against the objects the game will actually have: nothing sensible
## wants two words of the same family at once. A door has nobody to talk to,
## a person is not a place to go.
enum Slot { LOOK, HAND, ACT, REACH }

## Emitted after the character has reached this hotspot and acted on it. The
## verb is an int rather than Verb for the same reason as in VerbCoin.
##
## The character is carried along because with several playable characters
## "who did it" is half the answer: a door has to move the person who opened
## it, and picking something up has to put it in somebody's hands.
signal interacted(verb: int, character: PlayerCharacter)

## Emitted after an inventory item has been used on this hotspot, whether or
## not it was the item this hotspot was waiting for.
signal item_used(item: InventoryItem, character: PlayerCharacter)

## Said when a verb leads nowhere. Most objects in an adventure game refuse
## most of what is tried on them, and one generic line is how the genre has
## always covered it.
const REFUSAL: String = "Non mi sembra il caso."

## Said when the wrong item is used on this hotspot — which, given an inventory
## and a roomful of objects, is nearly every pairing the player will attempt.
const ITEM_REFUSAL: String = "Non c'entra niente con questo."

## The name the player sees. Kept apart from the node name so the node can
## stay an English identifier whatever language the game ends up speaking.
@export var display_name: String = ""

@export_group("Verbs")

## What this hotspot offers in the "holding" slot: TAKE, or nothing.
@export var hand_verb: Verb = Verb.NONE

## What it offers in the "do something to it" slot: USE, OPEN, CLOSE, or
## nothing.
@export var act_verb: Verb = Verb.NONE

## What it offers in the "where it leads, or who it is" slot: TALK, GO, or
## nothing.
@export var reach_verb: Verb = Verb.NONE

## What a press with no drag does. Most things are worth a look; a door is
## worth going through. Lifting the finger without having moved runs this,
## which is what makes the plain tap useful.
@export var default_verb: Verb = Verb.LOOK

@export_group("Texts")

## One line per slot rather than one per word, because a hotspot only ever has
## one word in each slot.
@export_multiline var look_text: String = ""
@export_multiline var hand_text: String = ""
@export_multiline var act_text: String = ""
@export_multiline var reach_text: String = ""

@export_group("What has happened since")

## Lines that take the place of the ones above while their conditions hold —
## how a hotspot remembers, through GameState, what was done to it before the
## room was thrown away and rebuilt.
##
## The first variant that both holds and has something to say for the slice
## being asked about wins. A variant may therefore fill in only the line it
## changes and leave the rest to fall through, and two variants may look after
## different slices under different conditions.
@export var variants: Array[HotspotVariant] = []

## All of these must hold for the hotspot to be in the room at all. Empty — the
## usual case — means it is always there.
##
## An absent hotspot is hidden and stops answering clicks, rather than being
## freed, so that it can come back when the conditions swing the other way.
## Note what "hidden" reaches: its own children. A hotspot whose picture is a
## sibling node goes on being visible while nothing responds to it, which is
## the wrong half. Put the picture under the hotspot.
##
## Worked out on entering the room and again whenever a flag is raised, a switch
## flips, or control passes to somebody else. Not on picking something up: a
## condition about what is in a pocket belongs in a variant or, later, in a line
## of dialogue, both of which are worked out afresh every time they are asked.
@export var present_if: PackedStringArray = PackedStringArray()

@export_group("Reaction to an item")

## The one item this hotspot does something about. One and not a list, for the
## same reason a hotspot has no script by default: a single expected item
## covers the ordinary lock-and-key case as data, and anything cleverer is a
## hotspot with a script of its own.
@export var accepted_item: InventoryItem = null

@export_multiline var accepted_text: String = ""

## Whether the item is used up. A key that opens a door is usually gone
## afterwards; a screwdriver is not.
@export var consumes_accepted_item: bool = true

## Raised when the accepted item is used, so the effect survives the room being
## thrown away and rebuilt. Optional: leave it empty for a hotspot whose
## reaction is only a line of text.
@export var accepted_flag: StringName = &""

# The collision layer this hotspot was authored with, so that one which is not
# currently there can be handed it back when it comes into being again.
var _own_collision_layer: int = 0

# Whether the hotspot is in the room right now. Starts true so that the first
# check applies the real answer precisely when it differs from the default.
var _present: bool = true


func _ready() -> void:
	_own_collision_layer = collision_layer

	# unbind() drops the arguments a signal carries. The answer is worked out
	# from scratch whatever changed, so there is nothing to do with the name of
	# the flag — and this way one method serves three signals of three different
	# shapes. There is no C# equivalent; a Callable in GDScript can be reshaped
	# before it is connected.
	#
	# Nothing is ever disconnected: Godot drops a connection when either end is
	# freed, and a hotspot is freed with its room.
	GameState.flag_raised.connect(_refresh_presence.unbind(1))
	GameState.switch_changed.connect(_refresh_presence.unbind(2))
	GameState.active_character_changed.connect(_refresh_presence.unbind(1))

	_refresh_presence()


## Whether this hotspot is in the room at all. Data covers the ordinary case;
## this is here to be overridden by a hotspot that comes and goes for a reason
## of its own, the way one holding an item that has been taken does.
func is_present() -> bool:
	return Conditions.all_hold(present_if, GameState.active_character)


func _refresh_presence() -> void:
	var present: bool = is_present()

	if present == _present:
		return

	_present = present
	visible = present

	# The layer is set deferred for the reason Game defers swapping rooms: a
	# flag can be raised in the middle of a physics step, because an action runs
	# when a walk ends and a walk ends inside _physics_process. Handing a shape
	# to the physics server while it is answering queries is not allowed.
	#
	# Zero and not the shape's disabled flag: a body on no layer at all is
	# matched by no query, and there may be more than one shape under a hotspot.
	set_deferred(&"collision_layer", _own_collision_layer if present else 0)


## The verb sitting in [param slot] on this hotspot, or NONE for an empty
## slice — which the coin then simply does not draw.
##
## Overridden by hotspots whose word depends on their state: a door offers
## OPEN or CLOSE from the same slot depending on how it stands. Note what is
## allowed to vary and what is not — the *word* follows visible state, but
## *whether the slot exists at all* is a fixed property of the object. A slice
## that appeared only when it would work would tell the player the answer.
func get_verb_for(slot: int) -> int:
	match slot:
		Slot.LOOK:
			return Verb.LOOK
		Slot.HAND:
			return hand_verb
		Slot.ACT:
			return act_verb
		Slot.REACH:
			return reach_verb

	return Verb.NONE


## The verb a press with no drag runs on this hotspot.
func get_default_verb() -> int:
	return default_verb


## The line to show for [param verb], or the generic refusal if this hotspot
## has nothing to say about it.
##
## Variants are consulted at the moment the question is asked, not when the room
## was built. Otherwise opening a door and then looking at it would give the
## description of a door that is still shut.
func get_text_for(verb: int) -> String:
	var slot: int = _slot_of(verb)

	if slot < 0:
		return REFUSAL

	var text: String = _variant_text(slot)

	if text.is_empty():
		text = _own_text(slot)

	return text if not text.is_empty() else REFUSAL


## Which slice [param verb] came out of, or -1 for a verb this hotspot does not
## offer. LOOK is not looked up: every hotspot is worth looking at.
func _slot_of(verb: int) -> int:
	if verb == Verb.LOOK:
		return Slot.LOOK

	# Checked before the comparisons below, or a verb of NONE would match every
	# empty slice this hotspot has.
	if verb == Verb.NONE:
		return -1

	if verb == get_verb_for(Slot.HAND):
		return Slot.HAND

	if verb == get_verb_for(Slot.ACT):
		return Slot.ACT

	if verb == get_verb_for(Slot.REACH):
		return Slot.REACH

	return -1


func _variant_text(slot: int) -> String:
	var character: PlayerCharacter = GameState.active_character

	for variant in variants:
		if variant == null or not variant.holds(character):
			continue

		var text: String = _text_of(variant, slot)
		if not text.is_empty():
			return text

	return ""


func _own_text(slot: int) -> String:
	match slot:
		Slot.LOOK:
			return look_text
		Slot.HAND:
			return hand_text
		Slot.ACT:
			return act_text
		Slot.REACH:
			return reach_text

	return ""


# Written out rather than shared with _own_text() through a table of property
# names. The two are four lines apart in the same file, so they cannot drift
# without it being obvious, and the slot enum stays the only thing that decides
# the order.
func _text_of(variant: HotspotVariant, slot: int) -> String:
	match slot:
		Slot.LOOK:
			return variant.look_text
		Slot.HAND:
			return variant.hand_text
		Slot.ACT:
			return variant.act_text
		Slot.REACH:
			return variant.reach_text

	return ""


## The line to show when [param item] is used on this hotspot.
func get_text_for_item(item: InventoryItem) -> String:
	if not accepts(item):
		return ITEM_REFUSAL

	return accepted_text if not accepted_text.is_empty() else REFUSAL


## True when [param item] is the one thing this hotspot is waiting for.
func accepts(item: InventoryItem) -> bool:
	return item != null and item == accepted_item


## Runs [param verb] on this hotspot, on behalf of [param character]. The text
## is the room's business; this is the hook for hotspots that actually do
## something, either by connecting to [signal interacted] or by overriding.
func interact(verb: int, character: PlayerCharacter) -> void:
	interacted.emit(verb, character)


## Uses [param item] on this hotspot, on behalf of [param character].
func use_item(item: InventoryItem, character: PlayerCharacter) -> void:
	if accepts(item):
		GameState.raise_flag(accepted_flag)

		if consumes_accepted_item and character != null:
			character.give_up(item)

	item_used.emit(item, character)


## The point the character should walk to before acting on this hotspot.
func get_approach_position() -> Vector2:
	# Looked up on the spot rather than held in an @onready field. It costs a
	# node lookup per interaction, which is nothing at the rate a player clicks,
	# and it keeps one more thing out of _ready() — which a subclass now has to
	# remember to call super() from, since presence is set up there.
	var marker: Node = get_node_or_null("ApproachPoint")

	# Without one the character would walk into the object itself — and some
	# hotspots, a door in a wall above all, sit outside the navigation mesh
	# entirely, so their own position is not a valid destination.
	if marker is Marker2D:
		return (marker as Marker2D).global_position

	return global_position
