class_name InventoryItem
extends Resource

## One thing a character can carry.
##
## A Resource, not a node: it is data with no place in the scene tree, and the
## same item can sit in an inventory, be named by a recipe and be expected by a
## hotspot without any of them owning it. Each item is a small .tres file under
## resources/items/, which is plain text and so can be written from anywhere.
##
## Two characters holding "the same" item hold the same resource — items are
## compared by identity, never copied. Nothing here changes at runtime, which
## is what makes that safe.

## Stable name used by flags and by anything that has to ask "has this been
## picked up yet". Keep it in English and never change it once it is in use:
## a saved flag refers to the id, not to the file.
@export var id: StringName = &""

## The name the player sees, in the inventory and in sentences about the item.
@export var display_name: String = ""

@export_multiline var look_text: String = ""

## Left empty for now. There is no art yet, so the inventory draws names; the
## slot will show this instead the day the sprites exist.
@export var icon: Texture2D = null
