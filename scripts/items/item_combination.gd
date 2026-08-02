class_name ItemCombination
extends Resource

## One recipe: two items that make a third.
##
## Deliberately not a field on [InventoryItem]. If an item carried its own
## recipes, the two classes would name each other and the project would be
## relying on GDScript resolving a cyclic reference — which it may well do, but
## it is not something that can be checked from the development machine. The
## recipes live in one book instead, and the arrow points one way only.

@export var first: InventoryItem = null
@export var second: InventoryItem = null

## What comes out. The two ingredients are taken away when it does.
@export var result: InventoryItem = null

## What the character says on success.
@export_multiline var text: String = ""


## True when this recipe is the pair [param a] and [param b], in either order.
func matches(a: InventoryItem, b: InventoryItem) -> bool:
	if first == null or second == null:
		return false

	return (first == a and second == b) or (first == b and second == a)
