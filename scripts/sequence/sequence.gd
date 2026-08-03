class_name Sequence
extends Resource

## A short scene that plays itself: the machine starts, the panel falls off, the
## character steps back and says something about it.
##
## The reason this exists at all is that until now the game could only say
## "something happened" — a line of caption, a flag, an item changing hands. It
## could not say "and then". A puzzle whose answer is correct but whose payoff
## is one sentence in a box reads as though nothing much happened, and the
## payoff is the part the player worked for.
##
## While one of these is running the game is not: the interface steps aside and
## the room stops listening, exactly as during a conversation. That is a promise
## to the player as much as an implementation detail — if something is going to
## happen on its own, taps in the meantime must not half-cancel it.

## The steps, in order. There is no branching and no condition: a scene that has
## to decide something is two scenes and a hotspot that chooses between them.
@export var steps: Array[SequenceStep] = []
