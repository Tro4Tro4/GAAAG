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
## the two things that belong to no piece: which item the player has in hand
## between choosing it in the bag and aiming it at something in the room, and
## the conversation currently going on, which outlives no room and belongs to
## no hotspot.

## What the bag button says when the player is not holding anything.
const BAG_LABEL: String = "UI_BAG"

## Shown when the bag closes with something in hand, so the half-written
## sentence is visible after the panel that started it has gone.
const USING_TEMPLATE: String = "UI_USING"

## Said after using the menu. The caption is the game's only voice, and there is
## no reason for saving to speak with a different one.
const SAVED: String = "UI_SAVED"
const SAVE_FAILED: String = "UI_SAVE_FAILED"
const LOADED: String = "UI_LOADED"
const LOAD_FAILED: String = "UI_LOAD_FAILED"
const NOTHING_TO_LOAD: String = "UI_NOTHING_TO_LOAD"

## Every recipe in the game. An @export filled in from Main.tscn rather than a
## preload: a mistyped path then costs a combination that refuses, instead of a
## game that will not start.
@export var combinations: CombinationBook = null

## Every item in the game, for turning the ids in a save back into things.
@export var catalogue: ItemCatalogue = null

## The noise a choice makes. One sound for the whole interface: a menu that
## clicks differently from a verb would be saying something it does not mean.
@export var ui_click: AudioStream = null

@onready var _room_container: Node2D = $RoomContainer
@onready var _caption: Caption = $UI/Caption
@onready var _verb_coin: VerbCoin = $UI/VerbCoin
@onready var _inventory_panel: InventoryPanel = $UI/InventoryPanel
@onready var _inventory_button: Button = $UI/InventoryButton
# Typed as the container it is rather than by a class_name of its own: all this
# node wants from the switch bar is to be able to put it away during a
# conversation, and character_bar.gd has never needed to be nameable.
@onready var _character_bar: HBoxContainer = $UI/CharacterBar
@onready var _dialogue_panel: DialoguePanel = $UI/DialoguePanel
@onready var _menu_button: Button = $UI/MenuButton
@onready var _menu_panel: MenuPanel = $UI/MenuPanel
@onready var _settings_panel: SettingsPanel = $UI/SettingsPanel
@onready var _title_screen: TitleScreen = $UI/TitleScreen
@onready var _fade: Fade = $UI/Fade
@onready var _camera: GameCamera = $Camera
@onready var _audio: AudioDirector = $Audio
@onready var _sequence: SequenceRunner = $Sequence

# The conversation going on, if any. A plain object rather than a node: it has
# nothing to draw, and one of them serves every conversation in the game.
var _dialogue: DialogueRunner = DialogueRunner.new()

# Who is doing the talking, kept only so they can be put back to standing still
# when the conversation ends.
var _talker: PlayerCharacter = null

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
	_verb_coin.aim_changed.connect(_on_aim_changed)

	_inventory_button.pressed.connect(_on_inventory_button_pressed)
	_inventory_panel.item_pressed.connect(_on_inventory_item_pressed)
	_inventory_panel.combine_requested.connect(_on_combine_requested)
	_inventory_panel.dismissed.connect(_on_inventory_dismissed)

	# The runner keeps the place in the conversation, the caption says the words
	# and the panel offers the answers: three pieces that never name each other.
	_dialogue.said.connect(_caption.show_speech)
	_dialogue.offered.connect(_dialogue_panel.show_options)
	_dialogue.finished.connect(_on_dialogue_finished)
	_dialogue_panel.option_selected.connect(_dialogue.choose)

	# The runner is told where to ask how long a line takes to read, so a scene
	# keeps pace with the reading speed rather than with a number in its code.
	_sequence.caption = _caption
	_sequence.wants_to_say.connect(_caption.show_text)
	_sequence.wants_to_play.connect(_audio.play_sound)
	_sequence.finished.connect(_on_sequence_finished)

	_menu_button.pressed.connect(_on_menu_button_pressed)
	_menu_panel.action_chosen.connect(_on_menu_action)
	_title_screen.action_chosen.connect(_on_title_action)

	# The bag button is written from here, so unlike the labels sitting in
	# Main.tscn it does not retranslate itself when the language changes.
	Settings.locale_changed.connect(_refresh_inventory_button)

	GameState.active_character_changed.connect(_on_active_character_changed)

	# Characters register during their own _ready(), and children are ready
	# before their parent, so the roster is already complete here and the
	# first character has already taken control without this node hearing it.
	for character in GameState.characters:
		character.room_changed.connect(_on_character_room_changed)

	_refresh_inventory_button()
	_show_room_of(GameState.active_character)

	# Last, and over a game that is already standing up. The title is an overlay,
	# not a scene of its own, so "Continua" has somewhere to load into instead of
	# having to start a game and then tell it what to become.
	if TitleScreen.should_ask():
		_set_ordinary_ui_visible(false)
		_title_screen.open()


func _on_active_character_changed(character: PlayerCharacter) -> void:
	_show_room_of(character)


func _on_character_room_changed(_character: PlayerCharacter) -> void:
	# Whoever walked through a door, the answer is the same: work out again
	# which room belongs on screen and who is standing in it.
	#
	# Behind a fade to black, which does two jobs at once. It is what makes
	# going through a door read as going somewhere rather than as a frame in
	# which the room was replaced — and the swap lands in a tween callback,
	# which is idle time. That last part is not cosmetic: a door is used at the
	# end of a walk, a walk ends inside a physics step, and taking every
	# hotspot's collision shape out of the world in the middle of one is not
	# allowed. The fade replaces the call_deferred that used to hold it.
	_fade.cover_then(_walk_through_door)


## Puts [param character]'s room on screen and hands the room over to them.
##
## Switching character takes you to that character, so the room on screen is
## always the active character's room. That is why nothing here remembers
## which room is shown: it is not a separate piece of state, it is a
## consequence of who you are controlling.
## The far side of a door: the new room goes up while the screen is black.
func _walk_through_door() -> void:
	_show_room_of(GameState.active_character)

	# After the room, so that what is written is the world as the player is
	# about to see it. Here and nowhere else: not at startup, which would
	# overwrite the very checkpoint an autosave exists to keep, and not on
	# switching character, where nothing has happened. Going through a door is
	# the one moment that is both a real change and a place worth coming back to.
	_autosave()


func _show_room_of(character: PlayerCharacter) -> void:
	if character == null:
		return

	# A menu still open, and an item still in hand, belonged to the errand you
	# have just walked away from. The item in particular came out of somebody
	# else's bag, and handing over control does not hand over their pockets.
	_verb_coin.close()
	_inventory_panel.close()
	_menu_panel.close()
	_release_held_item()

	if character.current_room != _room_path:
		_swap_room_to(character.current_room)

	_place_characters()

	if _room != null:
		_room.set_character(character)
		_camera.frame_room(_room.room_size)

		# Asked for on every showing, including coming back to a room already
		# playing it. The director is what knows that the same music twice over
		# is not a reason to start it again.
		_audio.play_music(_room.music)

	# After the room has been framed, or the first snap would be clamped to the
	# old room's edges.
	_camera.follow(character)


func _swap_room_to(room_path: String) -> void:
	# The invariant this whole arrangement rests on: exactly one room in the
	# tree, ever. It is checked and not assumed because when it breaks nothing
	# on screen explains it — see _sweep_stray_rooms().
	_sweep_stray_rooms()

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
	_room.wants_to_talk.connect(_on_wants_to_talk)
	_room.wants_to_play.connect(_audio.play_sound)
	_room.wants_to_run.connect(_on_wants_to_run)

	_room_container.add_child(_room)


## Throws out anything in RoomContainer that this node is not keeping track of.
##
## It cannot happen by way of _swap_room_to(), which takes the old room out of
## the tree before instancing the new one. The check is here anyway because the
## consequence is out of all proportion to the cause: every NavigationRegion2D
## in the tree feeds the same navigation map, so two rooms drawn at the same
## coordinates merge into one unusable mesh — a click snaps onto the other
## room's floor, or no path is found at all and nobody moves. It is the exact
## failure that rooms being swapped, rather than shown and hidden, exists to
## avoid, and it is worth more than the assumption that it cannot occur.
##
## Named in the warning and then cleared, rather than only reported: on screen
## two rooms look like one room with the wrong scenery in it, which explains
## nothing, and being unable to walk is worse than a line in the output.
func _sweep_stray_rooms() -> void:
	for child in _room_container.get_children():
		if child == _room:
			continue

		push_warning("RoomContainer held a room nobody was tracking, %s: thrown out. %s" % [
			child.name, "Two rooms in the tree stop anybody from walking."
		])

		_room_container.remove_child(child)
		child.queue_free()


func _place_characters() -> void:
	for character in GameState.characters:
		var is_here: bool = character.current_room == _room_path
		character.set_present(is_here)

		if not is_here or _room == null:
			continue

		# Before being put down, so that whoever is placed is already the size
		# this room draws people at that height.
		_room.hand_depth_to(character)

		# Only someone who has just come through a door has an entry to
		# consume. Everyone else stands where they were left.
		var entry: StringName = character.consume_pending_entry()
		if entry != &"":
			character.place_at(_room.get_entry_position(entry))


## Hands a scene over to the runner, with everything out of its way.
##
## The screen is blocked rather than the systems switched off one by one — the
## same trick the panels use, except that nothing is drawn. A scene that could
## be half-cancelled by a tap in the middle would be worse than no scene.
func _on_wants_to_run(sequence: Sequence, character: PlayerCharacter) -> void:
	_set_ordinary_ui_visible(false)
	_fade.block()
	_sequence.run(sequence, character, _room)


func _on_sequence_finished() -> void:
	_fade.unblock()
	_set_ordinary_ui_visible(true)


func _on_wants_to_talk(dialogue: Dialogue, character: PlayerCharacter) -> void:
	# The rest of the interface stands down for the duration. Not only because
	# you cannot wander off in the middle of being talked at: the panel swallows
	# every click while it is up, so the switch bar and the bag would be buttons
	# that do nothing, and a dead button is worse than an absent one.
	_set_ordinary_ui_visible(false)

	# Remembered so the state can be put back: the runner is handed nobody, on
	# purpose — a conversation is between the player and a line of text, and who
	# is standing there is the room's business.
	_talker = character
	if _talker != null:
		_talker.set_state(PlayerCharacter.State.TALKING)

	# Started last, because a conversation whose opening line offers nothing the
	# player can say is over before this call returns.
	_dialogue.start(dialogue, character)


func _on_dialogue_finished() -> void:
	if _talker != null and is_instance_valid(_talker):
		_talker.set_state(PlayerCharacter.State.IDLE)
	_talker = null

	_dialogue_panel.close()

	# Faded rather than cleared: the last thing said stays the couple of seconds
	# any other line would, instead of being taken away with the panel.
	_caption.fade()

	_set_ordinary_ui_visible(true)


## Everything that is only there while the player is actually playing. Hidden
## during a conversation, and while the title is up.
func _set_ordinary_ui_visible(is_ui_visible: bool) -> void:
	_character_bar.visible = is_ui_visible
	_inventory_button.visible = is_ui_visible
	_menu_button.visible = is_ui_visible


func _on_menu_button_pressed() -> void:
	if _menu_panel.is_open():
		_menu_panel.close()
		return

	_menu_panel.open()


func _on_menu_action(action: StringName) -> void:
	_audio.play_sound(ui_click)

	match action:
		MenuPanel.SAVE:
			_caption.show_text(SAVED if SaveGame.write(SaveGame.MANUAL_SLOT) else SAVE_FAILED)
		MenuPanel.LOAD:
			_load_from(SaveGame.MANUAL_SLOT)
		MenuPanel.LOAD_AUTO:
			_load_from(SaveGame.AUTO_SLOT)
		MenuPanel.SETTINGS:
			_settings_panel.open()
		MenuPanel.NEW_GAME:
			_start_new_game()
		MenuPanel.QUIT:
			get_tree().quit()


func _on_title_action(action: StringName) -> void:
	match action:
		TitleScreen.CONTINUE:
			_load_from(SaveGame.newest_slot())
			_leave_title()
		TitleScreen.NEW_GAME:
			# Nothing to reset: the title is only ever up over a game that has
			# just been built from its scenes, which is what a new game is.
			_leave_title()
		TitleScreen.SETTINGS:
			# The title stays underneath. Settings is drawn last of everything
			# in the interface, so it covers the title as it covers the room.
			_settings_panel.open()
		TitleScreen.QUIT:
			get_tree().quit()


func _leave_title() -> void:
	_title_screen.close()
	_set_ordinary_ui_visible(true)


func _load_from(slot: StringName) -> void:
	if not SaveGame.exists(slot):
		_caption.show_text(NOTHING_TO_LOAD)
		return

	if not SaveGame.restore(slot, catalogue):
		_caption.show_text(LOAD_FAILED)
		return

	# Behind the same fade a door uses, and for the better reason: the room on
	# screen was built for a world that no longer exists. Its hotspots worked
	# themselves out from flags that have just been replaced wholesale, and no
	# signal announced it, so it is thrown away and built again.
	_fade.cover_then(_finish_load)


func _finish_load() -> void:
	_reshow_room()
	_caption.show_text(LOADED)


func _start_new_game() -> void:
	GameState.clear()

	# Told not to ask again: somebody who has just chosen "new game" does not
	# want to be shown the title and asked the same question.
	TitleScreen.skip_once = true

	# The whole scene is built again rather than every character being put back
	# by hand: where somebody starts is written in Main.tscn and nowhere else,
	# so reloading is the only way that cannot get it wrong. The autoload
	# survives the reload, which is why it is emptied first.
	#
	# Deferred because this comes from inside an input event, and pulling the
	# tree out from under the node handling it is not a thing to do halfway.
	get_tree().reload_current_scene.call_deferred()


func _reshow_room() -> void:
	# Forgetting which room is on screen is what makes _show_room_of() rebuild
	# it even when the path has not changed. Blunt, but the alternative is a
	# second way into the same function, and there is only one caller.
	_room_path = ""
	_show_room_of(GameState.active_character)


func _autosave() -> void:
	SaveGame.write(SaveGame.AUTO_SLOT)


func _notification(what: int) -> void:
	# On a phone a game is rarely quit; it is swiped away, and this is the last
	# thing the engine says first. Not verifiable from the development machine,
	# which has nothing to suspend — if it never arrives, the autosave on going
	# through a door still stands on its own.
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		_autosave()


func _on_verb_chosen(verb: int, hotspot: Hotspot) -> void:
	_audio.play_sound(ui_click)

	if _room != null:
		_room.begin_action(verb, hotspot)


## Writes the word for the slice the finger is on. The badges show pictures,
## which say what a verb generally is; this is where the object's own word for
## it appears — and the top of the screen is the one place a finger never
## covers, so a long word costs nothing.
func _on_aim_changed(label: String) -> void:
	if label.is_empty():
		_caption.clear()
		return

	_caption.show_persistent(label)


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
		# Put together here rather than in the caption: a template with a name
		# in it needs both halves turned into words before they are joined.
		_caption.show_text(tr(USING_TEMPLATE) % tr(_held_item.display_name))


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
	_inventory_button.text = tr(_held_item.display_name) if _held_item != null else tr(BAG_LABEL)
