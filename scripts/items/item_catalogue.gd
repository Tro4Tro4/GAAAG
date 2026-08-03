class_name ItemCatalogue
extends Resource

## Every item in the game, in one file, so that a saved game can name one.
##
## A save cannot hold a resource, only a string, and the string it holds is the
## item's [member InventoryItem.id] — which was declared stable and never to be
## changed for exactly this day. Coming back the other way needs somewhere to
## look the id up, and this is it.
##
## The same shape as CombinationBook and for the same reason: one list, one
## place to look when something is not found. It has to be kept in step by hand
## — an item missing from here comes back from a save as nothing — and that is
## the accepted cost. The alternatives were worse: saving the file path instead
## of the id would break every save the day a file is renamed, and scanning the
## folder cannot be trusted in an exported project, where Godot converts the
## resources and the names on disk stop being the names written here.

@export var items: Array[InventoryItem] = []


## The item whose id is [param id], or null if the catalogue has not got one.
func find(id: StringName) -> InventoryItem:
	for item in items:
		if item != null and item.id == id:
			return item

	return null
