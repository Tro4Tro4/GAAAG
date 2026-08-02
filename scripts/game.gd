extends Node2D

## The root of the running game: it holds what must outlive a room.
##
## Rooms are swapped in and out of RoomContainer. The characters and the
## interface are not — they are children of this node for the whole session.
## That is the entire point: a character standing in a room you are not looking
## at has to keep existing, or the switch bar could only ever offer you the
## people in front of you, and Day of the Tentacle switching would be
## impossible.
##
## This node owns no state. Who is active, what has happened and who is
## carrying what stay in GameState and in the characters. Game is only the
## place in the tree where the pieces are held and wired to each other — plus
## the one thing that belongs to no piece: which item the player has in hand
## between choosing it in the bag and aiming it at something in the room.

## What the bag button says when the player is not holding anything.
const BAG_LABEL: String = "Zaino"

## Shown when the bag closes with something in hand, so the half-written
## sentence is visible after the panel that started it has gone.
const USING_TEMPLATE: String = "Usa %s con..."

## Every recipe in the game. An @export filled in from Main.tscn rather than a
## preload: a mistyped path then costs a combination that refuses, instead of a
## game that will not start.
@export var combinations: CombinationBook = null

@onready var _room_container: Node2D = $RoomContainer
@onready var _caption: Caption = $UI/Caption
@onready var _verb_coin: VerbCoin = $UI/VerbCoin
@onready var _inventory_panel: InventoryPanel = $UI/InventoryPanel
@onready var _inventory_button: Button = $UI/InventoryButton

# The room currently in the tree, and the scene file it came from. The path is
# what tells a real room change from switching to someone standing next to you.
var _room: Room = null
var _room_path: String = ""

# The item taken out of the bag and not yet aimed at anything. It lives here
# and not in the character because it is not something the character has — it
# is a sentence the player has started and can still abandon.
var _held_item: InventoryItem = null


func _ready() -> void:
	_verb_coin.verb_chosen.connect(_on_verb_chosen)
	_verb_coin.item_verb_chosen.connect(_on_item_verb_chosen)

	_inventory_button.pressed.connect(_on_inventory_button_pressed)
	_inventory_panel.item_pressed.connect(_on_inventory_item_pressed)
	_inventory_panel.combine_requested.connect(_on_combine_requested)
	_inventory_panel.dismissed.connect(_on_inventory_dismissed)

	GameState.active_character_changed.connect(_on_active_character_changed)

	# Characters register during their own _ready(), and children are ready
	# before their parent, so the roster is already complete here and the
	# first character has already taken control without this node hearing it.
	for character in GameState.characters:
		character.room_changed.connect(_on_character_room_changed)

	_refresh_inventory_button()
	_show_room_of(GameState.active_character)


func _on_active_character_changed(character: PlayerCharacter) -> void:
	_show_room_of(character)


func _on_character_room_changed(_character: PlayerCharacter) -> void:
	# Whoever walked through a door, the answer is the same: work out again
	# which room belongs on screen and who is standing in it.
	#
	# Deferred because of where this call comes from. A door is used at the end
	# of a walk, and the walk ends inside _physics_process — so this runs while
	# the engine is in the middle of a physics step, and swapping rooms means
	# taking every hotspot's collision shape out of the world and putting a new
	# set in. Deferring holds that until the step is over.
	_show_room_of.call_deferred(GameState.active_character)


## Puts [param character]'s room on screen and hands the room over to them.
##
## Switching character takes you to that character, so the room on screen is
## always the active character's room. That is why nothing here remembers
## which room is shown: it is not a separate piece of state, it is a
## consequence of who you are controlling.
func _show_room_of(character: PlayerCharacter) -> void:
	if character == null:
		return

	# A menu still open, and an item still in hand, belonged to the errand you
	# have just walked away from. The item in particular came out of somebody
	# else's bag, and handing over control does not hand over their pockets.
	_verb_coin.close()
	_inventory_panel.close()
	_release_held_item()

	if character.current_room != _room_path:
		_swap_room_to(character.current_room)

	_place_characters()

	if _room != null:
		_room.set_character(character)


func _swap_room_to(room_path: String) -> void:
	if _room != null:
		# remove_child() before queue_free(), and not queue_free() alone:
		# freeing is deferred to the end of the frame, so the outgoing room's
		# NavigationRegion2D would still be in the tree next to the incoming
		# one. Every 2D navigation region in the tree feeds the same navigation
		# map, and a map holding two rooms at the same coordinates can snap a
		# click onto the other room's floor.
		_room_container.remove_child(_room)
		_room.queue_free()
		_room = null

	_room_path = room_path

	if room_path.is_empty():
		push_warning("No room to show: the character has an empty current_room.")
		return

	var scene: PackedScene = load(room_path)
	if scene == null:
		push_error("Could not load room scene: %s" % room_path)
		return

	# "as Room" and not a bare assignment: instantiate() is typed as Node, and
	# GDScript refuses to narrow that on its own. Unlike a C# cast this one
	# does not throw — it yields null if the scene's root is not a Room, which
	# the next lines would then report as a missing method rather than a crash.
	_room = scene.instantiate() as Room
	if _room == null:
		push_error("Room scene %s does not have a Room as its root." % room_path)
		return

	# Connected straight to the interface: the room says what it wants said and
	# which hotspot was tapped, and knows nothing about the nodes that answer.
	# No disconnect anywhere — Godot drops a connection when either end is
	# freed, and the room is freed above.
	_room.wants_to_say.connect(_caption.show_text)
	_room.hotspot_activated.connect(_verb_coin.open_for)
	_room.held_item_released.connect(_release_held_item)

	_room_container.add_child(_room)


func _place_characters() -> void:
	for character in GameState.characters:
		var is_here: bool = character.current_room == _room_path
		character.set_present(is_here)

		if not is_here or _room == null:
			continue

		# Only someone who has just come through a door has an entry to
		# consume. Everyone else stands where they were left.
		var entry: StringName = character.consume_pending_entry()
		if entry != &"":
			character.place_at(_room.get_entry_position(entry))


func _on_verb_chosen(verb: int, hotspot: Hotspot) -> void:
	if _room != null:
		_room.begin_action(verb, hotspot)


func _on_inventory_button_pressed() -> void:
	if _inventory_panel.is_open():
		_inventory_panel.close()
		_on_inventory_dismissed()
		return

	_inventory_panel.open()


func _on_inventory_item_pressed(item: InventoryItem, at_screen_position: Vector2) -> void:
	_verb_coin.open_for_item(item, at_screen_position)


## Answers a verb aimed at something in the bag. Nothing walks anywhere: an
## item is already in the character's hands, so there is nowhere to walk to.
func _on_item_verb_chosen(verb: int, item: InventoryItem) -> void:
	match verb:
		Hotspot.Verb.LOOK:
			_caption.show_text(item.look_text if not item.look_text.is_empty() else Hotspot.REFUSAL)
		Hotspot.Verb.USE:
			# USE on an item does not use it on anything yet — it picks it up
			# ready to be aimed. The other half of the sentence is the next
			# thing tapped, in the bag or in the room.
			_hold_item(item)
		_:
			_caption.show_text(Hotspot.REFUSAL)


func _on_combine_requested(first: InventoryItem, second: InventoryItem) -> void:
	# The same item twice is the player pressing what they are holding: that
	# means putting it back, not combining it with itself.
	if first == second:
		_release_held_item()
		return

	var recipe: ItemCombination = null
	if combinations != null:
		recipe = combinations.find(first, second)
	else:
		push_warning("Game has no combination book: every combination will refuse.")

	var character: PlayerCharacter = GameState.active_character

	if recipe == null or recipe.result == null or character == null:
		_caption.show_text(CombinationBook.REFUSAL)
		_release_held_item()
		return

	character.give_up(first)
	character.give_up(second)
	character.take(recipe.result)

	_caption.show_text(recipe.text)
	_release_held_item()


func _on_inventory_dismissed() -> void:
	if _held_item != null:
		_caption.show_text(USING_TEMPLATE % _held_item.display_name)


func _hold_item(item: InventoryItem) -> void:
	_held_item = item
	_inventory_panel.set_held_item(item)
	_refresh_inventory_button()

	if _room != null:
		_room.set_held_item(item)


func _release_held_item() -> void:
	if _held_item == null:
		return

	_held_item = null
	_inventory_panel.set_held_item(null)
	_refresh_inventory_button()

	if _room != null:
		_room.set_held_item(null)


func _refresh_inventory_button() -> void:
	# The button doubles as the only place the held item is always visible: the
	# bag is shut most of the time the player is carrying something out to use.
	_inventory_button.text = _held_item.display_name if _held_item != null else BAG_LABEL
