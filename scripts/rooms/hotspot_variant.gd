class_name HotspotVariant
extends Resource

## A set of lines a hotspot uses instead of its own, while its conditions hold.
##
## This is how a room remembers what happened in it. A room is thrown away when
## the player walks out and built again from its scene file when they come back,
## so a crate that has been emptied, a panel that has been unscrewed and a door
## that stands open all have to work out again, from GameState, what they are
## supposed to say. A variant is that reasoning written as data instead of as a
## script per object.
##
## Only the lines vary, never which verbs the hotspot offers. That is deliberate
## and is the rule stated in CLAUDE.md: a word may follow state the player can
## already see — a door says Apri or Chiudi — but a slice that appeared only
## when it would work would be telling the player the answer. A hotspot whose
## words really must change with its state is a hotspot with a script, the way
## DoorHotspot is.
##
## Note that this class does not mention Hotspot anywhere, and holds four plain
## lines rather than a slot-to-text lookup. Hotspot names HotspotVariant, so if
## HotspotVariant named Hotspot back the project would depend on how GDScript
## resolves a cyclic reference between two class_name scripts — which it
## probably handles, but which cannot be checked from the development machine.
## The same reasoning put every recipe in one CombinationBook.

## All of these must hold for this variant to be in force. See [Conditions] for
## the grammar. An empty list always holds, which makes such a variant a plain
## override rather than a mistake.
@export var conditions: PackedStringArray = PackedStringArray()

@export_multiline var look_text: String = ""
@export_multiline var hand_text: String = ""
@export_multiline var act_text: String = ""
@export_multiline var reach_text: String = ""


## True when this variant is currently in force for [param character].
func holds(character: PlayerCharacter) -> bool:
	return Conditions.all_hold(conditions, character)
