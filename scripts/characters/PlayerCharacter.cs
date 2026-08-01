using Godot;

namespace Aggga;

/// <summary>
/// A character that walks to a point when told to.
///
/// Pathfinding is delegated to a NavigationAgent2D: the room hands over a
/// destination, the agent returns the next corner of the computed path, and
/// this script only steers towards that corner. Walking around obstacles is
/// therefore a property of the room's navigation mesh, not of this code.
/// </summary>
public partial class PlayerCharacter : CharacterBody2D
{
    /// <summary>
    /// Emitted once, when the character stops on its destination. Nothing
    /// listens to it yet; it is what "walk to the hotspot, then act on it"
    /// will hang off once hotspots exist.
    /// </summary>
    [Signal]
    public delegate void DestinationReachedEventHandler();

    // Pixels per second, expressed at the game's 384x216 base resolution.
    [Export] private float _walkSpeed = 55f;

    // Assigned in the editor rather than looked up by string path: a path
    // breaks silently the moment the node is renamed or moved.
    [Export] private NavigationAgent2D _agent = null!;

    // True while a destination is pending. Without it, DestinationReached
    // would fire on every frame the character spends standing still.
    private bool _isWalking;

    /// <summary>Sends the character to <paramref name="globalTarget"/>.</summary>
    public void WalkTo(Vector2 globalTarget)
    {
        // TargetPosition is in global coordinates, not local to this node.
        _agent.TargetPosition = globalTarget;
        _isWalking = true;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_isWalking)
            return;

        if (_agent.IsNavigationFinished())
        {
            StopWalking();
            return;
        }

        // The agent returns the next corner of the path, never the final
        // destination directly: steering corner by corner is what makes the
        // character go around an obstacle instead of into it.
        Vector2 nextCorner = _agent.GetNextPathPosition();
        Velocity = GlobalPosition.DirectionTo(nextCorner) * _walkSpeed;

        // MoveAndSlide applies Velocity using the physics frame time on its
        // own, which is why `delta` is not multiplied in here.
        MoveAndSlide();
    }

    private void StopWalking()
    {
        _isWalking = false;
        Velocity = Vector2.Zero;
        EmitSignal(SignalName.DestinationReached);
    }
}
