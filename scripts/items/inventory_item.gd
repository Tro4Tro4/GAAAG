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

## Shown in the inventory slot, to the left of the name. 12x12 px, drawn by
## tools/make_item_icons.py — the slot is 16 units tall and a Button adds the
## theme's padding, so anything larger pushes the slot out of shape.
##
## May be left null: a slot with no icon shows its name alone, which is how the
## panel worked before there was any art.
@export var icon: Texture2D = null
