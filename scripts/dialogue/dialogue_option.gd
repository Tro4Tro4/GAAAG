class_name DialogueOption
extends Resource

## One thing the player may say, and what comes of saying it.
##
## Conditions decide whether it is offered at all, and they are the same strings
## used everywhere else in the game — see [Conditions]. That is the whole point
## of having written that grammar first: a line of dialogue that only appears
## once somebody has the screwdriver is spelled exactly like a hotspot that only
## appears once somebody has the screwdriver.
##
## There is deliberately no "ask this only once" switch. It is already
## expressible, and expressing it costs two fields that are here anyway:
## [codeblock]
## conditions = ["!asked_about_badge"]
## raises     = ["asked_about_badge"]
## [/codeblock]
## A dedicated flag would have to be derived from something — the option's
## position in the list, or its text — and both change when the conversation is
## edited, which is precisely when a "once" must not quietly reset.

## What the player says. Shown on a button, so keep it to a line: at font size 8
## the panel is 352 pixels wide, which is about seventy characters.
@export var text: String = ""

## All of these must hold for the option to be offered.
@export var conditions: PackedStringArray = PackedStringArray()

## What the other one answers. Used only when the conversation stays where it
## is — see [member goes_to], which supersedes it.
@export_multiline var reply: String = ""

## The id of the line to move to. Left empty, the conversation stays put and the
## options are worked out again, which is what makes a list of topics behave the
## way the genre expects.
##
## Arriving somewhere says that line's own opening; staying says [member reply].
## Setting both is a mistake and is reported, because only one of the two can be
## on screen.
@export var goes_to: StringName = &""

@export_group("What it does")

## Flags raised on choosing this. The general way for a conversation to leave a
## mark on the world: a hotspot elsewhere can be waiting on the same name.
@export var raises: PackedStringArray = PackedStringArray()

## Handed to whoever is doing the talking. Null for the ordinary option that
## only says something.
@export var gives: InventoryItem = null

## Whether the conversation is over once the reply has been said. A line that
## offers nothing the player can currently say ends by itself, so this is only
## needed for a deliberate goodbye among options that would otherwise go on.
@export var ends: bool = false
