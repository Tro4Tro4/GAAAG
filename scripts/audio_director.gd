class_name AudioDirector
extends Node

## The one thing that makes a noise.
##
## Three players, and no more than three: one for whatever the room sounds like,
## one for whatever just happened, one for the feet. It was two for a long time,
## on the grounds that an adventure of this kind never has more going on at once
## — and footsteps are what falsified that. They are the only sound in the game
## that is continuous and involuntary; everything else is discrete and caused by
## the player. Sharing one player between them means the most frequent and least
## informative sound in the game interrupts the rarest and most meaningful ones:
## pick something up, tap to walk away, and the first footfall cuts the thud.
##
## This is still not a pool of voices, which remains infrastructure bought
## against a need nobody has. It is one more named player for one named job, and
## the next sound that wants its own has to make the same argument.
##
## It lives next to the characters and the camera rather than inside a room,
## because music that stopped and started again every time somebody walked
## through a door would be worse than no music.
##
## The sounds in assets/audio are placeholders generated from a script — a
## click, a thud, a chime and two building hums. They are there so the wiring
## can be heard rather than believed; replacing them is replacing files.

## Buses, so that music and effects can be turned down separately. Declared in
## default_bus_layout.tres, which is the one place Godot looks.
const MUSIC_BUS: StringName = &"Music"
const SOUND_BUS: StringName = &"Sound"

@onready var _music: AudioStreamPlayer = $Music
@onready var _sound: AudioStreamPlayer = $Sound
@onready var _steps: AudioStreamPlayer = $Steps

# What the music player is currently on, so that asking for the same music
# twice — which happens every time a room is rebuilt — does not restart it.
var _music_stream: AudioStream = null


func _ready() -> void:
	_music.bus = MUSIC_BUS
	_sound.bus = SOUND_BUS
	# The feet share the effects bus rather than getting a third one: the buses
	# exist so the player can turn music and effects down separately, and nobody
	# wants a slider for their own shoes.
	_steps.bus = SOUND_BUS

	# Looped by hand rather than by the import setting: whether a .wav comes out
	# of Godot's importer with looping on depends on an .import file the editor
	# writes, and this project cannot check that from here. Restarting it when
	# it ends works whatever the importer decided.
	_music.finished.connect(_repeat)

	Settings.volumes_changed.connect(_apply_volumes)
	_apply_volumes()


## Plays [param stream] as the music, or stops it if null. Asking for what is
## already playing does nothing at all.
func play_music(stream: AudioStream) -> void:
	if stream == _music_stream:
		return

	_music_stream = stream

	if stream == null:
		_music.stop()
		return

	_music.stream = stream
	_music.play()


## Plays [param stream] once, over whatever else is going on.
func play_sound(stream: AudioStream) -> void:
	if stream == null:
		return

	_sound.stream = stream
	_sound.play()


## Plays [param stream] as a footfall, on the player kept for them.
##
## Separate from [method play_sound] so that walking never interrupts anything
## that matters, and so that nothing that matters interrupts the walking either.
func play_step(stream: AudioStream) -> void:
	if stream == null:
		return

	_steps.stream = stream
	_steps.play()


func _repeat() -> void:
	if _music_stream != null:
		_music.play()


func _apply_volumes() -> void:
	_set_bus(MUSIC_BUS, Settings.music_volume)
	_set_bus(SOUND_BUS, Settings.sound_volume)


func _set_bus(bus: StringName, volume: float) -> void:
	var index: int = AudioServer.get_bus_index(bus)

	if index < 0:
		push_warning("There is no audio bus called %s; check default_bus_layout.tres." % bus)
		return

	# Silence is its own case: linear_to_db(0) is minus infinity, and a bus told
	# to be minus infinity loud is not reliably silent. Muting says it plainly.
	AudioServer.set_bus_mute(index, is_zero_approx(volume))
	AudioServer.set_bus_volume_db(index, linear_to_db(maxf(volume, 0.001)))
