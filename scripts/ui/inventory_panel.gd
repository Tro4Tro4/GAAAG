class_name InventoryPanel
extends Control

## The bag, shown only when the player asks for it.
##
## Hidden by default and opened with a button. On a screen 216 pixels tall a
## permanent strip of items would cost a tenth of the room for something the
## player looks at rarely, so it costs nothing until it is wanted and covers
## the middle of the screen while it is.
##
## Slots are built from the active character's inventory every time it changes.
## Each character carries their own bag, so opening the panel after switching
## shows a different set — that is the point, not a side effect.
##
## Input works exactly as in VerbCoin, and for the same reason: the panel reads
## raw events in _input() and hit-tests the slots itself, while the slot buttons
## are visuals with MOUSE_FILTER_IGNORE that never see an event. It also means
## a press on a slot is caught on the way *down*, which is what lets the
## verb-coin's press-and-drag gesture start from a slot at all — a Button only
## reports itself once the finger has already come back up.

## Emitted when a slot is pressed with nothing in hand: the verb-coin opens
## on it. The position is where to open it.
signal item_pressed(item: InventoryItem, at_screen_position: Vector2)

## Emitted when a second item is pressed while one is already in hand.
signal combine_requested(first: InventoryItem, second: InventoryItem)

## Emitted when the panel is dismissed by pressing outside it.
signal dismissed

## Slots per row. Three fits the frame at this resolution without the names
## being cut short.
const COLUMNS: int = 3

const SLOT_FONT_SIZE: int = 8
const SLOT_MINIMUM_SIZE: Vector2 = Vector2(88, 16)

@onready var _frame: Panel = $Frame
@onready var _slots: GridContainer = $Frame/Slots
@onready var _empty_label: Label = $Frame/Empty

# The item the player has picked up off the panel and is about to use. Held
# here as well as in Game because the slot for it is drawn differently, and
# because pressing it a second time is how the player changes their mind.
var _held_item: InventoryItem = null

# The character whose bag is on show, kept so its signal can be dropped when
# control passes to somebody else.
var _character: PlayerCharacter = null


func _ready() -> void:
	visible = false
	_slots.columns = COLUMNS

	GameState.active_character_changed.connect(_on_active_character_changed)
	_on_active_character_changed(GameState.active_character)


func open() -> void:
	_rebuild()
	visible = true


func close() -> void:
	visible = false


func is_open() -> bool:
	return visible


## Tells the panel which item is in hand, so its slot can show it.
func set_held_item(item: InventoryItem) -> void:
	if item == _held_item:
		return

	_held_item = item
	_rebuild()


func _on_active_character_changed(character: PlayerCharacter) -> void:
	if _character != null and is_instance_valid(_character):
		_character.inventory_changed.disconnect(_on_inventory_changed)

	_character = character

	if _character != null:
		_character.inventory_changed.connect(_on_inventory_changed)

	_rebuild()


func _on_inventory_changed(_character_that_changed: PlayerCharacter) -> void:
	_rebuild()


func _input(event: InputEvent) -> void:
	if not visible:
		return

	# Only the press matters. The release belongs to whatever the press
	# started — the verb-coin gesture, most of the time — and the coin is
	# already open and eating events by then.
	if not event is InputEventMouseButton:
		return

	var button_event: InputEventMouseButton = event
	if not button_event.pressed or button_event.button_index != MOUSE_BUTTON_LEFT:
		return

	# Read straight from the event, with no conversion. See the note at the top
	# of verb_coin.gd for what happens otherwise.
	var pressed_slot: Button = _slot_at(button_event.position)

	if pressed_slot != null:
		_press_slot(pressed_slot)
	elif not _frame.get_global_rect().has_point(button_event.position):
		# Outside the frame means "that's enough". The press is swallowed all
		# the same, so putting the panel away never also pokes whatever was
		# behind it.
		close()
		dismissed.emit()

	get_viewport().set_input_as_handled()


func _press_slot(slot: Button) -> void:
	var item: InventoryItem = slot.get_meta(&"item") as InventoryItem
	if item == null:
		return

	if _held_item == null:
		item_pressed.emit(item, slot.get_global_rect().get_center())
		return

	# Pressing the item already in hand puts it back down; pressing a different
	# one asks for the two to be put together.
	if item == _held_item:
		combine_requested.emit(_held_item, _held_item)
	else:
		combine_requested.emit(_held_item, item)


## The slot under [param point], or null. Global rects, not local ones: slots
## live inside a GridContainer inside the frame, so their own position is
## relative to the grid and says nothing about where they are on screen.
func _slot_at(point: Vector2) -> Button:
	for child in _slots.get_children():
		var slot := child as Button
		if slot != null and slot.get_global_rect().has_point(point):
			return slot

	return null


func _rebuild() -> void:
	for child in _slots.get_children():
		_slots.remove_child(child)
		child.queue_free()

	var items: Array[InventoryItem] = []
	if _character != null:
		items = _character.inventory

	_empty_label.visible = items.is_empty()

	for item in items:
		_slots.add_child(_make_slot(item))


func _make_slot(item: InventoryItem) -> Button:
	var slot := Button.new()
	slot.text = item.display_name
	slot.custom_minimum_size = SLOT_MINIMUM_SIZE
	slot.add_theme_font_size_override("font_size", SLOT_FONT_SIZE)
	slot.focus_mode = Control.FOCUS_NONE
	slot.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Same trick as the verb-coin: a toggled Button draws itself in its pressed
	# style, so the item in hand looks picked up without a second set of art.
	slot.toggle_mode = true
	slot.button_pressed = item == _held_item

	# The slot has to be able to say which item it is, and a Button has nowhere
	# to put that. Metadata is Godot's answer for exactly this: a name-value
	# pair hung on any Object, which here saves keeping a parallel array in
	# step with the children of a container that is rebuilt from scratch.
	slot.set_meta(&"item", item)

	return slot
