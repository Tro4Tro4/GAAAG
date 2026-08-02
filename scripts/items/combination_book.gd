class_name CombinationBook
extends Resource

## Every recipe in the game, in one file.
##
## A single list rather than a rule scattered over the items it involves: when
## a combination does not work, there is one place to look, and adding one is
## adding a line to a text file instead of editing two resources that have to
## agree with each other.

## Said when two items have nothing to do with each other, which is the answer
## for almost every pair anyone will ever try.
const REFUSAL: String = "Insieme non fanno assolutamente niente."

@export var recipes: Array[ItemCombination] = []


## The recipe for [param a] plus [param b], or null if there is not one.
func find(a: InventoryItem, b: InventoryItem) -> ItemCombination:
	if a == null or b == null or a == b:
		return null

	for recipe in recipes:
		if recipe != null and recipe.matches(a, b):
			return recipe

	return null
