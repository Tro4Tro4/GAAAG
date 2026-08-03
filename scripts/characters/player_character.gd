class_name PlayerCharacter
extends CharacterBody2D

## A character that walks to a point when told to.
##
## Pathfinding is delegated to a NavigationAgent2D: the room hands over a
## destination, the agent returns the next corner of the computed path, and
## this script only steers towards that corner. Walking around obstacles is
## therefore a property of the room's navigation mesh, not of this code.
##
## Characters are children of Game, not of a room, and live for the whole
## session. A character whose room is not on screen is hidden and stops
## processing, but never leaves the tree — which is why its position needs no
## saving anywhere, and why it stays on the switch bar while it is elsewhere.

## Emitted once, when the character stops on its destination. The room listens
## to it to run the verb the player chose.
signal destination_reached

## Emitted when this character has gone through a door. Game listens, and puts
## the new room on screen if this is the character the player is controlling.
signal room_changed(character: PlayerCharacter)

## Emitted when this character picks something up or parts with it, so the
## inventory panel can redraw without being told who did what.
signal inventory_changed(character: PlayerCharacter)

## The four ways a character can be turned. Four and not eight because that is
## what a sprite sheet of this kind of game holds, and because a diagonal walk
## in a room this size is over before anybody has read it.
enum Facing { DOWN, LEFT, RIGHT, UP }

## What the character is doing, which is what an animation would be chosen by.
enum State { IDLE, WALKING, TALKING }

## The name shown on the character-switching bar.
@export var display_name: String = ""

## This character's drawings. Every character shares one scene and differs only
## by the sheet it is given, so a new character costs a resource and not a node.
##
## The sheet holds nine animations, named <state>_<direction> with the
## directions down, side and up: left is the side flipped, which is why there
## are three drawings for four ways of facing.
@export var frames: SpriteFrames

## Pixels per second, expressed at the game's 384x216 base resolution.
@export var walk_speed: float = 55.0

## The scene file of the room this character is standing in: set here for the
## room they start in, and changed by walking through a door. It is the only
## record of where anybody is — there is no separate table of positions,
## because the character node itself is never unloaded.
@export_file("*.tscn") var current_room: String = ""

## Which way the character is turned. Kept when they stop: somebody who walked
## off to the left is still facing left while standing there.
var facing: int = Facing.DOWN

## What the character is doing. Set from outside for talking, because only the
## thing running the conversation knows when one is on.
var state: int = State.IDLE

# The room's perspective: between these two heights the character is drawn
# between these two sizes. Flat by default, so a room that says nothing about
# depth gets a character that does not change size.
var _depth_top_y: float = 0.0
var _depth_bottom_y: float = 0.0
var _depth_top_scale: float = 1.0
var _depth_bottom_scale: float = 1.0

## What this character is carrying. One bag each, not one bag for everybody:
## an object that has to get from one person to another is then a puzzle
## instead of a formality, which is the reason the game has several characters
## in the first place.
var inventory: Array[InventoryItem] = []

@onready var _visual: Node2D = $Visual
@onready var _sprite: AnimatedSprite2D = $Visual/Sprite

# Resolved with @onready rather than @export: a node reference written by
# hand into a .tscn is not reliably resolved, and the agent is part of this
# same scene anyway, so renaming it means editing this scene regardless.
@onready var _agent: NavigationAgent2D = $NavigationAgent2D

# True while a destination is pending. Without it, destination_reached would
# fire on every frame the character spends standing still.
var _is_walking: bool = false

# Where this character should be put down when its room next comes on screen.
# Empty for anyone who did not just come through a door.
var _pending_entry: StringName = &""


func _ready() -> void:
	_sprite.sprite_frames = frames
	_refresh_visual()
	GameState.register_character(self)


func _exit_tree() -> void:
	# A safety net rather than a mechanism: characters are meant to outlive
	# every room. Should one ever be freed anyway, it must not stay on the
	# roster and leave a dead button on the switch bar.
	GameState.unregister_character(self)


## Sends the character to [param global_target].
func walk_to(global_target: Vector2) -> void:
	# target_position is in global coordinates, not local to this node.
	_agent.target_position = global_target
	_is_walking = true
	set_state(State.WALKING)


## Moves the character to another room, to arrive at [param entry_name].
func move_to_room(room_path: String, entry_name: StringName) -> void:
	_cancel_walk()
	current_room = room_path
	_pending_entry = entry_name
	room_changed.emit(self)


## Takes on the perspective of the room the character is standing in. Told
## rather than asked: a character is not a child of a room and has no way to
## find one, which is the same arrangement that lets them outlive it.
func set_depth(top_y: float, bottom_y: float, top_scale: float, bottom_scale: float) -> void:
	_depth_top_y = top_y
	_depth_bottom_y = bottom_y
	_depth_top_scale = top_scale
	_depth_bottom_scale = bottom_scale

	_refresh_visual()


## Turns the character towards [param point]. Used on arriving at a hotspot:
## having walked round to the front of something, standing with your back to it
## is worse than not having walked at all.
func face_towards(point: Vector2) -> void:
	var towards: Vector2 = point - global_position

	if towards.is_zero_approx():
		return

	# Whichever axis the thing is further along wins. A character mostly to the
	# side of you is looked at sideways even if they are also a little above.
	if absf(towards.x) >= absf(towards.y):
		facing = Facing.RIGHT if towards.x > 0.0 else Facing.LEFT
	else:
		facing = Facing.DOWN if towards.y > 0.0 else Facing.UP

	_refresh_visual()


## Says what the character is doing. Walking sets itself; talking has to be
## told, because only whatever is running the conversation knows.
func set_state(new_state: int) -> void:
	if new_state == state:
		return

	state = new_state
	_refresh_visual()


## True when this character is carrying [param item].
func is_carrying(item: InventoryItem) -> bool:
	return item != null and item in inventory


## Adds [param item] to this character's inventory.
func take(item: InventoryItem) -> void:
	if item == null or item in inventory:
		return

	inventory.append(item)
	inventory_changed.emit(self)


## Removes [param item] from this character's inventory.
func give_up(item: InventoryItem) -> void:
	if not item in inventory:
		return

	inventory.erase(item)
	inventory_changed.emit(self)


## Everything about this character that a saved game has to remember.
##
## The position is in here because a character node is never unloaded and so
## nothing else holds it — which was the point of that arrangement, and is the
## reason there is no table of positions anywhere to save instead.
func capture() -> Dictionary:
	return {
		&"room": current_room,
		&"position": global_position,
		&"inventory": inventory.duplicate(),
	}


## Puts this character back as a save found them. The items arrive already
## resolved: turning ids into resources is [SaveGame]'s business, not a
## character's.
func restore(room: String, at: Vector2, carried: Array[InventoryItem]) -> void:
	current_room = room
	inventory = carried

	# Nobody loaded from a file has just come through a door, so any entry owed
	# from before the load has to go — otherwise the first time this character's
	# room comes on screen they would be teleported to a doorway.
	_pending_entry = &""

	place_at(at)
	inventory_changed.emit(self)


## Returns the entry point owed to this character, and forgets it. Empty when
## the character did not arrive through a door.
func consume_pending_entry() -> StringName:
	var entry: StringName = _pending_entry
	_pending_entry = &""
	return entry


## Puts the character down at [param new_position], cancelling any walk.
func place_at(new_position: Vector2) -> void:
	_cancel_walk()
	global_position = new_position

	# Put down somewhere else means a different height, which in a room with
	# perspective means a different size. Without this a character dropped at
	# the back of a room would keep the size they had at the front until the
	# first step they took.
	_refresh_visual()


## Shows or hides the character according to whether its room is on screen.
##
## Hiding alone would not be enough: visibility does not stop _physics_process,
## so a hidden character would go on walking across a navigation mesh that is
## no longer loaded. PROCESS_MODE_DISABLED stops the node and its children.
func set_present(is_present: bool) -> void:
	visible = is_present
	process_mode = Node.PROCESS_MODE_INHERIT if is_present else Node.PROCESS_MODE_DISABLED

	if not is_present:
		_cancel_walk()


func _physics_process(delta: float) -> void:
	if not _is_walking:
		return

	if _agent.is_navigation_finished():
		_stop_walking()
		return

	# The agent returns the next corner of the path, never the final
	# destination directly: steering corner by corner is what makes the
	# character go around an obstacle instead of into it.
	var next_corner: Vector2 = _agent.get_next_path_position()
	velocity = global_position.direction_to(next_corner) * walk_speed

	_face_along(velocity)
	_refresh_visual()

	# move_and_slide() applies velocity using the physics frame time on its
	# own, which is why delta is not multiplied in here.
	move_and_slide()


func _stop_walking() -> void:
	_cancel_walk()
	destination_reached.emit()


## Turns the character the way they are going. Only while walking: a character
## standing still keeps whichever way they were last pointed.
func _face_along(direction: Vector2) -> void:
	if direction.is_zero_approx():
		return

	if absf(direction.x) >= absf(direction.y):
		facing = Facing.RIGHT if direction.x > 0.0 else Facing.LEFT
	else:
		facing = Facing.DOWN if direction.y > 0.0 else Facing.UP


## Chooses the drawing that says which way the character is turned and what they
## are doing. This is the whole of what facing and state are for: everything
## else in this script works out those two values, and this turns them into a
## name.
func _refresh_visual() -> void:
	# Called from _ready() before the first frame and from _physics_process
	# after, so the nodes are always there by now — but a character can be
	# turned by a save being loaded before it has entered the tree.
	if _sprite == null:
		return

	var direction: String = "down"
	match facing:
		Facing.LEFT, Facing.RIGHT:
			direction = "side"
		Facing.UP:
			direction = "up"

	var doing: String = "idle"
	if state == State.WALKING:
		doing = "walk"
	elif state == State.TALKING:
		doing = "talk"

	# The side is drawn facing right and mirrored for the left, which halves the
	# drawing. It works because nothing about these characters is asymmetric —
	# a bag on one shoulder would end the trick.
	_sprite.flip_h = facing == Facing.LEFT

	var wanted: StringName = StringName(doing + "_" + direction)
	if _sprite.animation != wanted or not _sprite.is_playing():
		_sprite.play(wanted)

	# Only the picture is scaled, never the node: the collision shape and the
	# navigation agent are how big the character is *as a thing in the room*,
	# and perspective is about how big they look.
	_visual.scale = Vector2.ONE * _depth_scale()


## How big the character is at the height they are standing at. A straight line
## between the room's two reference heights, and flat outside them — walking off
## the top of the floor should not make anybody vanish.
func _depth_scale() -> float:
	if is_equal_approx(_depth_top_y, _depth_bottom_y):
		return 1.0

	var along: float = clampf(
		(global_position.y - _depth_top_y) / (_depth_bottom_y - _depth_top_y), 0.0, 1.0
	)

	return lerpf(_depth_top_scale, _depth_bottom_scale, along)


func _cancel_walk() -> void:
	# Silent, unlike _stop_walking(): destination_reached would run the room's
	# pending action, and a walk is cancelled precisely when that room is
	# about to stop being the one on screen.
	_is_walking = false
	velocity = Vector2.ZERO

	if state == State.WALKING:
		set_state(State.IDLE)
